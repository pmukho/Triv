from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio
import redis.asyncio as redis
from pydantic import BaseModel, Field
import psycopg2
import os
import datetime

DB_CONFIG = {
    "dbname": os.environ.get("POSTGRES_DB"),
    "user": os.environ.get("POSTGRES_USER"),
    "password": os.environ.get("POSTGRES_PASSWORD"),
    "host": "postgres-db",
    "port": "5432"
}

def get_db_connection():
    conn = psycopg2.connect(**DB_CONFIG)
    return conn

redis_client = None

class _GameBatchReqElem(BaseModel):
    category: str
    count: int

class GameBatchReq(BaseModel):
    user_id: str
    batch_size: int
    batch: list[_GameBatchReqElem]

class Question(BaseModel):
    id: str
    category: str
    hint1: str
    hint2: str
    hint3: str
    answer: str
    created_at: datetime.datetime
    usage_count: int

class GameBatchResp(BaseModel):
    batch: list[Question]

async def notify_qgen():
    while True:
        # just looking at ouput of docker-compose up, its not entire clear
        # that print stmts are coming from this function until some 
        # endpoint is hit (print messages are buffered until then)
        print("Notifying QGen", datetime.datetime.now())
        # make request to QGen here (prob need to connect to some global/traffic related state here)
        await asyncio.sleep(5)

@asynccontextmanager
async def lifespan(app):
    print("Starting up")

    # background task that runs periodically
    asyncio.create_task(notify_qgen())

    global redis_client
    redis_client = await redis.from_url("redis://redis:6379/0")

    yield
    print("Shutting down")

    await redis.aclose()

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def read_root():
    return {"message": "Deployment of QAStore with FastAPI"}

@app.post("/getbatch/")
async def serve_game_batch(batch_req: GameBatchReq):
    # check cache for unseen q's for client
    # if none, get new batch from db

    user_id = batch_req.user_id
    async with redis_client.pipeline(transaction=True) as pipe:
        for elem in batch_req.batch:
            category = elem.category
            count = elem.count
            cache_key = f"unseen:{user_id}:{elem.category}"
            pipe.lrange(cache_key, 0, count-1)
        cached_results = await pipe.execute()
    print(f"Cached results: {cached_results}")

    queries = []
    params = []
    for elem in batch_req.batch:
        print(elem)
        query = f"""
            SELECT *
            FROM questions q
            LEFT JOIN user_question_store uqs ON q.id = uqs.question_id AND uqs.user_id = %s
            WHERE uqs.question_id IS NULL
            AND q.category = %s
            LIMIT %s
        """
        queries.append(query)
        # request extra questions to cache for later
        params.extend([user_id, elem.category, batch_req.batch_size])
    query = " UNION ALL ".join(queries)
    print(query)
    print(params)
    
    questions = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        questions = cursor.fetchall()
        print(f"Questions from DB: {questions}")
    except Exception as e:
        print(e)
        return {"error": "Failed to fetch questions"}
    finally:
        cursor.close()
        conn.close()
    
    # cache excess questions
    return_qs = []
    counts = {elem.category: elem.count for elem in batch_req.batch}
    async with redis_client.pipeline(transaction=True) as pipe:
        for q in questions:
            q = Question(
                id=q[0],
                category=q[1],
                hint1=q[2],
                hint2=q[3],
                hint3=q[4],
                answer=q[5],
                created_at=q[6],
                usage_count=q[7]
            )
            if counts[q.category] > 0:
                return_qs.append(q)
                counts[q.category] -= 1
            else:
                cache_key = f"unseen:{user_id}:{q.category}"
                pipe.rpush(cache_key, q.id)
                pipe.set(f"question:{q.id}", q.json())
        await pipe.execute()

    return GameBatchResp(batch=return_qs)
