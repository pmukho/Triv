from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import redis.asyncio as redis
from psycopg2 import pool
import os
from models import _GameBatchReqElem, GameBatchReq, Question, GameBatchResp, DownvoteBatchReq
from contextlib import contextmanager

# Database connection related settings
db_name = os.environ.get("POSTGRES_DB")
db_user = os.environ.get("POSTGRES_USER")
db_password = os.environ.get("POSTGRES_PASSWORD")
db_host = "postgres-db"
db_port = "5432"
MAX_DB_CONNECTIONS = 5
MIN_DB_CONNECTIONS = 1

db_conn_pool = pool.SimpleConnectionPool(
    minconn=MIN_DB_CONNECTIONS,
    maxconn=MAX_DB_CONNECTIONS,
    user=db_user,
    password=db_password,
    host=db_host,
    port=db_port
)
@contextmanager
def get_db_connection():
    conn = db_conn_pool.getconn()
    try:
        yield conn
    finally:
        conn.close()
        db_conn_pool.putconn(conn)


@asynccontextmanager
async def lifespan(app):
    print("Starting up")

    global redis_client
    redis_client = await redis.from_url("redis://redis:6379/0")

    yield
    print("Shutting down")

    await redis.aclose()

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost"],
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"]
)

@app.get("/")
async def read_root():
    return {"message": "Deployment of Cache with FastAPI"}

async def get_redis_batch(batch_req: GameBatchReq):
    print("CHECKING CACHE")
    user_id = batch_req.user_id
    async with redis_client.pipeline(transaction=True) as pipe:
        for elem in batch_req.batch:
            count = elem.count
            cache_key = f"unseen:{user_id}:{elem.category}"
            pipe.lrange(cache_key, 0, count-1)
            pipe.ltrim(cache_key, count, -1) # remove the unseen questions from cache
        cached_results = await pipe.execute()
    print(f"Cached results: {cached_results}")

    # see how many questions we need to fetch from db
    counts = {elem.category: elem.count for elem in batch_req.batch}
    return_qs = []
    for i in range(0, len(cached_results), 2):
        for q in cached_results[i]:
            q = q.decode()
            q = Question.parse_raw(q)
            return_qs.append(q)

            if counts[q.category] > 0:
                counts[q.category] -= 1
                if counts[q.category] == 0:
                    del counts[q.category]

    fwd_batch_req = GameBatchReq(
        user_id=user_id,
        batch_size=batch_req.batch_size,
        batch=[_GameBatchReqElem(category=k, count=v) for k, v in counts.items()]
    )

    return return_qs, fwd_batch_req

async def get_db_batch(batch_req: GameBatchReq):
    print("CHECKING DB")
    user_id = batch_req.user_id
    queries = []
    params = []
    for elem in batch_req.batch:
        query = f"""
            (SELECT *
            FROM questions q
            LEFT JOIN user_question_store uqs 
                ON q.id = uqs.question_id 
                AND uqs.user_id = %s
            WHERE uqs.question_id IS NULL
                AND q.category = %s
            LIMIT %s)
        """
        queries.append(query)
        params.extend([user_id, elem.category, elem.count])       
    query = " UNION ALL ".join(queries)
    print("Query: ", query)
    
    questions = []
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        questions = cursor.fetchall()
        print("Fetched questions: ", questions)
        questions = [Question(
            id=q[0],
            category=q[1],
            hint1=q[2],
            hint2=q[3],
            hint3=q[4],
            answer=q[5],
            created_at=q[6],
            usage_count=q[7],
            downvotes=q[8]
        ) for q in questions]

        # split questions into return and excess
        return_qs = []
        excess_qs = []
        counts = {elem.category: elem.count for elem in batch_req.batch}
        for q in questions:
            if counts[q.category] > 0:
                counts[q.category] -= 1
                return_qs.append(q)
            else:
                excess_qs.append(q)
        # cache excess questions
        print("Caching excess questions: ", excess_qs)
        async with redis_client.pipeline(transaction=True) as pipe:
            for q in excess_qs:
                cache_key = f"unseen:{user_id}:{q.category}"
                pipe.rpush(cache_key, q.json())
            await pipe.execute()
        # return the questions
        return return_qs

    # try:
    #     conn = get_db_connection()
    #     cursor = conn.cursor()
    #     cursor.execute(query, params)
    #     questions = cursor.fetchall()
    #     print("Fetched questions: ", questions)
    #     questions = [Question(
    #         id=q[0],
    #         category=q[1],
    #         hint1=q[2],
    #         hint2=q[3],
    #         hint3=q[4],
    #         answer=q[5],
    #         created_at=q[6],
    #         usage_count=q[7],
    #         downvotes=q[8]
    #     ) for q in questions]

    #     # split questions into return and excess
    #     return_qs = []
    #     excess_qs = []
    #     counts = {elem.category: elem.count for elem in batch_req.batch}
    #     for q in questions:
    #         if counts[q.category] > 0:
    #             counts[q.category] -= 1
    #             return_qs.append(q)
    #         else:
    #             excess_qs.append(q)

    #     # cache excess questions
    #     print("Caching excess questions: ", excess_qs)
    #     async with redis_client.pipeline(transaction=True) as pipe:
    #         for q in excess_qs:
    #             cache_key = f"unseen:{user_id}:{q.category}"
    #             pipe.rpush(cache_key, q.json())
    #         await pipe.execute()

    #     # return the questions
    #     return return_qs
    # except Exception as e:
    #     print(e)
    #     print({"error": "Failed to fetch questions"})
    #     return []
    # finally:
    #     try:
    #         cursor.close()
    #         conn.close()
    #     except NameError:
    #         pass

@app.post("/getbatch/")
async def serve_game_batch(batch_req: GameBatchReq):
    # check cache for unseen q's for client
    # if none, get new batch from db

    cached_qs, fwd_req = await get_redis_batch(batch_req)
    print("FWD REQ: ", fwd_req)
    if len(fwd_req.batch) == 0:
        return GameBatchResp(batch=cached_qs)

    db_results = await get_db_batch(fwd_req)
    print("DB RESULTS: ", db_results)
    print("CACHED QS: ", cached_qs)
    return GameBatchResp(batch=cached_qs + db_results)

@app.post("/downvote/")
async def downvote_questions(downvote_req: DownvoteBatchReq):
    # update database records
    print("Downvoting questions: ", downvote_req)
    placeholders = ",".join(["%s"] * len(downvote_req.batch))
    query = f"""
        UPDATE questions
        SET downvote_count = downvote_count + 1
        WHERE id IN ({placeholders})"""
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, downvote_req.batch)
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(e)
        return {"error": "Failed to downvote questions"}
    return {"status": "success"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}