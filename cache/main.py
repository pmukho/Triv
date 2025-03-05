from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager, contextmanager
import redis.asyncio as redis
from psycopg2 import pool
import os
from models import _GameBatchReqElem, GameBatchReq, Question, GameBatchResp, DownvoteBatchReq
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.executors.pool import ThreadPoolExecutor
import datetime
import httpx

# Database connection related settings
db_name = os.environ.get("POSTGRES_DB")
db_user = os.environ.get("POSTGRES_USER")
db_password = os.environ.get("POSTGRES_PASSWORD")
db_host = "postgres-db"
db_port = "5432"
MAX_DB_CONNECTIONS = 5
MIN_DB_CONNECTIONS = 1

db_conn_pool = pool.ThreadedConnectionPool(
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
        db_conn_pool.putconn(conn)

# Redis connection related settings
MAX_REDIS_CONNECTIONS = 10
redis_host = "redis"
redis_port = 6379
redis_client = None

# Scheduled background tasks that will run periodically on separate thread
executors = {
    "default": ThreadPoolExecutor(1)
}
scheduler = BackgroundScheduler(
    executors=executors,
    job_defaults={"misfire_grace_time": 60},
    timezone="UTC"
)

DOWNVOTE_THRESHOLD = os.environ.get("DOWNVOTE_THRESHOLD", 3)
USAGE_THRESHOLD = os.environ.get("USAGE_THRESHOLD", 5)
DB_EVICT_PERIOD = os.environ.get("DB_EVICT_PERIOD", 5) # in minutes
def evict_questions_from_db():
    print("Checking for questions to evict")

    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = """
            DELETE FROM questions
            WHERE 
                usage_count >= %s OR 
                downvote_count >= %s OR
                created_at < NOW() - Interval '2 days';
        """
        cursor.execute(query, (USAGE_THRESHOLD, DOWNVOTE_THRESHOLD))
        conn.commit()
        cursor.close()

CATEGORIES = [] # set by lifespan start
MIN_THRESHOLD_FACTOR = os.environ.get("MIN_THRESHOLD_FACTOR", 0.1)
PROACTIVE_FETCH_COUNT = os.environ.get("PROACTIVE_FETCH_COUNT", 5)
QGEN_BATCH_SIZE = os.environ.get("QGEN_BATCH_SIZE", 10)
GENERATE_CHECK_PERIOD = os.environ.get("GENERATE_CHECK_PERIOD", 5) # in minutes
def generate_questions_as_needed():
    print("Checking counts per category")

    # Fetch category counts for questions and articles
    question_counts = {}
    article_counts = {}
    fetch_batch = []
    with get_db_connection() as conn, conn.cursor() as cursor:
        # Assumes that the number of questions marked for eviction is small
        query = """
            SELECT category, COUNT(*) FROM questions
            GROUP BY category;
        """
        cursor.execute(query)
        q_counts = cursor.fetchall()
        for cat, count in q_counts:
            question_counts[cat] = count

        query = """
            SELECT category, COUNT(*) FROM wiki_articles
            WHERE 
                last_used IS NULL OR
                last_used < NOW() - INTERVAL '1 day'
                GROUP BY category;
            """
        cursor.execute(query)
        a_counts = cursor.fetchall()
        for cat, count in a_counts:
            article_counts[cat] = count

        # See if we need to generate more questions
        for cat in CATEGORIES:
            a_count = article_counts.get(cat, None)
            if a_count is None:
                print(f"Category {cat} exhausted for articles")
                continue
            
            min_threshold = max(int(MIN_THRESHOLD_FACTOR * a_count), 1)
            q_count = question_counts.get(cat, 0)
            if q_count < min_threshold:
                print(f"Category {cat} needs more questions: {q_count} < {min_threshold}")
                query = """
                    SELECT title FROM wiki_articles
                    WHERE 
                        category = %s AND
                        (last_used IS NULL OR
                        last_used < NOW() - INTERVAL '1 day')
                    LIMIT %s;
                """

                cursor.execute(query, (cat, PROACTIVE_FETCH_COUNT))
                articles = cursor.fetchall()
                articles = [a[0] for a in articles]
                fetch_batch.extend([(title, cat) for title in articles])
    
    # Fetch questions for articles
    for i in range(0, len(fetch_batch), QGEN_BATCH_SIZE):
        batch = fetch_batch[i:i+QGEN_BATCH_SIZE]
        # will be schedule to run right away
        scheduler.add_job(
            fetch_and_store_questions,
            args=(batch,),
            replace_existing=False,
            misfire_grace_time=None, # will run eventually
        )

def fetch_and_store_questions(title_category_batch):
    print("Fetching questions for articles")
    print(title_category_batch)
    titles = [t[0] for t in title_category_batch]
    categories = [t[1] for t in title_category_batch]
    payload = {
        "article_names": titles,
    }

    # using synchronous client to avoid overloading question-gen
    questions = []
    with httpx.Client(timeout=httpx.Timeout(120.0, connect=10.0)) as client:
        try:
            response = client.post("http://question-gen:8000/questions", json=payload)
            response.raise_for_status()
            questions = response.json()["questions"]
            print("Fetched questions: ", questions)
        except Exception as e:
            print("Error fetching questions: ", e)
            return
        
    # Store questions in database
    with get_db_connection() as conn, conn.cursor() as cursor:
        placeholders = ",".join(["(%s, %s, %s, %s, %s, %s)"] * len(questions))
        query = f"""
            INSERT INTO questions (id, category, hint1, hint2, hint3, answer) VALUES
            {placeholders}
            """
        params = []
        for i in range(len(questions)):
            q = questions[i]
            title = titles[i]
            category = categories[i]
            params.extend([
                title,
                category,
                q["prompt1"],
                q["prompt2"],
                q["prompt3"],
                q["answer"]
            ])
        cursor.execute(query, params)
        conn.commit()

        # Update last_used for articles
        placeholders = ",".join(["%s"] * len(titles))
        query = f"""
            UPDATE wiki_articles
            SET last_used = NOW()
            WHERE title IN ({placeholders});
        """
        cursor.execute(query, titles)
        conn.commit()

# FastAPI app
@asynccontextmanager
async def lifespan(app):
    print("Starting up")

    # Initialize Redis client (no need to manage connection pool)
    global redis_client
    redis_pool = redis.connection.BlockingConnectionPool(
        max_connections=MAX_REDIS_CONNECTIONS,
        host=redis_host,
        port=redis_port,
        decode_responses=True
    )
    redis_client = redis.Redis(connection_pool=redis_pool)
    # Test Redis connection
    try:
        await redis_client.ping()
        print("Connected to Redis")
    except redis.ConnectionError:
        print("Failed to connect to Redis")
        raise

    # Test database connection
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            print("Connected to PostgreSQL")
            cursor.close()
    except Exception as e:
        print("Failed to connect to PostgreSQL", e)
        raise

    # Fetch categories from databse
    print("Fetching categories")
    global CATEGORIES
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT category FROM wiki_articles")
        CATEGORIES = cursor.fetchall()
        CATEGORIES = [c[0] for c in CATEGORIES]
        cursor.close()
    print("Categories: ", CATEGORIES)

    # Start background scheduler
    scheduler.add_job(
        evict_questions_from_db,
        trigger=IntervalTrigger(minutes=DB_EVICT_PERIOD),
        id="evict_questions",
        replace_existing=False,
    )
    scheduler.add_job(
        generate_questions_as_needed,
        trigger=IntervalTrigger(minutes=GENERATE_CHECK_PERIOD),
        next_run_time=datetime.datetime.now(), # run right away, then periodically
        id="generate_questions",
        replace_existing=False,
    )
    scheduler.start()

    yield

    print("Shutting down")
    db_conn_pool.closeall()
    await redis_client.aclose()
    scheduler.shutdown(wait=False)

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost"],
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"]
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    return await log_request_middleware(request, call_next)

@app.get("/")
async def read_root():
    return {"message": "Deployment of Cache with FastAPI"}

async def get_redis_batch(batch_req: GameBatchReq):
    logger.info("CHECKING CACHE")

    # print("CHECKING CACHE")
    user_id = batch_req.user_id
    async with redis_client.pipeline(transaction=True) as pipe:
        for elem in batch_req.batch:
            count = elem.count
            cache_key = f"unseen:{user_id}:{elem.category}"
            pipe.lrange(cache_key, 0, count-1)
            pipe.ltrim(cache_key, count, -1) # remove the unseen questions from cache
        cached_results = await pipe.execute()
    # print(f"Cached results: {cached_results}")
    logger.debug(f"Cached results: {cached_results}")


    # see how many questions we need to fetch from db
    counts = {elem.category: elem.count for elem in batch_req.batch}
    return_qs = []
    for i in range(0, len(cached_results), 2):
        for q in cached_results[i]:
            print(q)
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

async def get_db_batch(batch_req: GameBatchReq, fetch_count: int = 10):
    print("CHECKING DB")
    user_id = batch_req.user_id
    queries = []
    params = []
    for elem in batch_req.batch:
        query = f"""
            (SELECT * FROM questions q
            LEFT JOIN user_question_store uqs
                ON q.id = uqs.question_id
                AND uqs.user_id = %s
            WHERE uqs.question_id IS NULL
                AND q.category = %s
            LIMIT %s)
        """
        queries.append(query)
        params.extend([user_id, elem.category, max(fetch_count, elem.count)])       
    query = " UNION ALL ".join(queries)
    
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

        # update usage count
        placeholders = ",".join(["%s"] * len(questions))
        query = f"""
            UPDATE questions
            SET usage_count = usage_count + 1
            WHERE id IN ({placeholders})
        """
        params = [q.id for q in questions]
        cursor.execute(query, params)

        # update user_quesiton_store
        placeholders = ",".join(["(%s, %s)"] * len(questions))
        query = f"""
            INSERT INTO user_question_store (user_id, question_id) VALUES 
            {placeholders}
        """
        params = [ item for q in questions for item in (user_id, q.id) ]
        cursor.execute(query, params)
        conn.commit()
        cursor.close()

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
        logger.info(f"Caching excess questions: {excess_qs}")
        # print("Caching excess questions: ", excess_qs)
        async with redis_client.pipeline(transaction=True) as pipe:
            for q in excess_qs:
                cache_key = f"unseen:{user_id}:{q.category}"
                pipe.rpush(cache_key, q.json())
            await pipe.execute()

        return return_qs

@app.post("/getbatch/")
async def serve_game_batch(batch_req: GameBatchReq):
    # check cache for unseen q's for client
    # if none, get new batch from db

    cached_qs, fwd_req = await get_redis_batch(batch_req)
    print("FWD REQ: ", fwd_req)
    if len(fwd_req.batch) == 0:
        logger.info("All questions found in cache")
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
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, downvote_req.batch)
        conn.commit()
        cursor.close()
    return {"status": "success"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}