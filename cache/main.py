from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio
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

class _GameBatchReqElem(BaseModel):
    category: str
    count: int

class GameBatchReq(BaseModel):
    user_id: str
    batch_size: int
    batch: list[_GameBatchReqElem]

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
    # Run at startup
    print("Starting up")
    asyncio.create_task(notify_qgen())
    yield
    # Run at shutdown
    print("Shutting down")

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def read_root():
    return {"message": "Deployment of QAStore with FastAPI"}

@app.post("/getbatch/")
async def serve_game_batch(batch_req: GameBatchReq):
    # check cache for unseen q's for client
    # if none, get new batch from db

    user_id = batch_req.user_id
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
        params.extend([user_id, elem.category, elem.count])
    query = " UNION ALL ".join(queries)
    print(query)
    print(params)
    
    questions = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        questions = cursor.fetchall()
        cursor.close()
        conn.close()
    except Exception as e:
        print(e)
        questions = []

    return questions
