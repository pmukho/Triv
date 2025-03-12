from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from gmfactory import GmFactory
import json
import psycopg2
import os
from pydantic import BaseModel

tags_metadata = [
    {
        "name": "health",
        "description": "Health check for the API"
    },
    {
        "name": "leaderboard",
        "description": "Get the leaderboard for the game"
    },
    {
        "name": "login",
        "description": "Login to the game"
    }
]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost","http://localhost:80"],
    allow_methods=["POST,GET"],
    allow_headers=["*"],
)

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


class ConnectionManager:
    """
    A class to manage websocket connections for clients.

    Attributes
    ----------
    active_connections : dict
        A dictionary to store active websocket connections with client_id as key.

    Methods
    -------
    connect(client_id: int, websocket: WebSocket)
        Accepts a new websocket connection and adds it to the active connections.
    disconnect(client_id: int)
        Removes a websocket connection from the active connections.
    send_message(client_id: int, message: dict)
        Sends a message to a specific client.
    broadcast(message: dict)
        Sends a message to all connected clients.
    """
    def __init__(self):
        self.active_connections: dict[int, WebSocket] = {}

    async def connect(self, client_id: int, websocket: WebSocket):
        if client_id not in self.active_connections:
            await websocket.accept()
            self.active_connections[client_id] = websocket
        print(f"Client {client_id} connected.")

    def disconnect(self, client_id: int):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            print(f"Client {client_id} disconnected.")

    async def send_message(self, client_id: int, message: dict):
        ws = self.active_connections.get(client_id)
        if ws:
            await ws.send_json(message)
            
    async def broadcast(self, message: dict):
        for ws in self.active_connections.values():
            await ws.send_json(message)

    
gmFactory = GmFactory()
manager = ConnectionManager()

hint_tasks = {}
@app.websocket("/ws/quiz/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    """
    WebSocket endpoint for handling quiz game interactions.

    Expects messages from client including "start_question", "submit_answer", "end_game", and "downvote_question".
    Handles sending hints and receiving answers from the client.

    Parameters
    ----------
    websocket : WebSocket
        The WebSocket connection object.

    client_id : int
        The unique identifier for the client.
    """
    # Connect the client
    await manager.connect(client_id, websocket)
    
    max_questions = int(websocket.query_params.get("max_questions", 5))
    gm_key = gmFactory.get_or_create_game_master(client_id, max_questions)
    gm = gmFactory.game_masters[gm_key]

    try:
        while True:
            # Wait for a message from the client
            message = await websocket.receive_text()
            data = json.loads(message)

            msg_type = data.get("type")
            payload = data.get("payload", {})

            if msg_type == "start_question":
                if hint_tasks.get(client_id):
                    hint_tasks[client_id].cancel()

                # Send hints as a background task
                task = asyncio.create_task(send_hints_timed(gm, client_id, categorySelect=payload))
                hint_tasks[client_id] = task
                
                await manager.send_message(client_id, {
                    "type": "game_status",
                    "status": "Started question"
                })
            elif msg_type == "submit_answer":
                user_answer = payload.get("answer", "")
                hintsUsed = payload.get("hintCount", 0)
                print(f"Received answer from client {client_id}: {user_answer} with {hintsUsed} hints used")
                is_correct, score, answer, hints = await gm.check_answer(user_answer, hintsUsed)
                await manager.send_message(client_id, {
                    "type": "answer_result",
                    "correct": is_correct,
                    "score": score,
                    "answer": answer,
                    "hints": hints
                })
                # Cancel any timer
                hint_tasks[client_id].cancel()
            elif msg_type == "end_game":
                print('GAME ENDED')
                await gmFactory.end_game(client_id)
                if hint_tasks.get(client_id):
                    hint_tasks[client_id].cancel()
                    hint_tasks.pop(client_id, None)

                print('status sent')
            elif msg_type == "downvote_question":
                q_id = gm.downvote_question()
                print(f"GM Downvoted question {q_id}")
                await manager.send_message(client_id, {
                    "type": "game_status",
                    "status": f"Downvoted question {q_id}"
                })

    # Handle disconnect and other errors
    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        print(f"Error in WebSocket communication with client {client_id}: {e}")
        await websocket.close()


async def send_hints_timed(game_master, client_id: int, categorySelect):

    """
    Sends hints to the client at timed intervals.
    
    Parameters
    ----------
    game_master : GameMaster
        The game master instance managing the game state.
    client_id : int
        The unique identifier for the client.
    """
    try:
        # Fetch hints
        while True:
            hints, has_question = await game_master.get_hints(categorySelect)
            if has_question and len(hints) >= 3:
                break

            # Wait & retry
            print(f"No questions available for client {client_id}. Retrying in 5s...")
            await asyncio.sleep(5)

        # Immediately send hint #1
        await manager.send_message(client_id, {
            "type": "hint",
            "hint": hints[0]
        })
        await asyncio.sleep(10)

        # Send hint #2
        await manager.send_message(client_id, {
            "type": "hint",
            "hint": hints[1]
        })
        await asyncio.sleep(10)

        # Send hint #3
        await manager.send_message(client_id, {
            "type": "hint",
            "hint": hints[2]
        })
    except asyncio.CancelledError:
        # if the user ended the game or answered early
        print(f"send_hints_timed task cancelled for client {client_id}")
    except Exception as e:
        print(f"Error sending hints to client {client_id}: {e}")



class LoginData(BaseModel):
    username: str
    client_id: str
@app.post('/ws/login')
async def login(data: LoginData, tags=["login"]):
    """
    Login endpoint for the game.

    Parameters
    ----------
    data : LoginData
        The login data containing the username and client_id.

    Returns
    -------
    dict
        A dictionary containing the login status and message.
    """
    print(f"Logging in user {data.username} with client_id {data.client_id},", flush=True) 
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT username, id FROM users WHERE id = %s", (data.client_id,))
        user = cursor.fetchone()
        print("User is:",user, flush=True)
        if user:
            if user[0] != data.username:
                cursor.execute("UPDATE users SET username = %s WHERE id = %s", (data.username, data.client_id))
                conn.commit()
                print("Username updated", flush=True)
            print("User found", flush=True)
            return {"ok": True,"status": "User found, Username changed"}
        else:
            print("User not found, creating new user", flush=True)
            cursor.execute("INSERT INTO users (username, id) VALUES (%s, %s) RETURNING id", (data.username, data.client_id))
            print("User created", flush=True)
            conn.commit()
            return {"ok": True,"status": "User found, Username changed"}
    except Exception as e:
        print(f"Error logging in: {str(e)}", flush=True)
        return {"ok":False,"error": "Internal server error"}, 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.get('/ws/leaderboard/get_leaderboard')
async def get_leaderboard(tags=["leaderboard"]):
    """
    Get the leaderboard for the game.

    Returns
    -------
    dict
        A dictionary containing the leaderboard data.
    """
    try:
        print("Getting leaderboard", flush=True)
        conn = get_db_connection()
        cursor = conn.cursor()
        leaderboard = """
        SELECT users.username, game_results.score
        FROM game_results
        JOIN users ON game_results.user_id = users.id
        ORDER BY game_results.score DESC
        LIMIT 10
        """
        cursor.execute(leaderboard)
        results = cursor.fetchall()
        print({"data": results}, flush=True)
        leaderboard_data = [
            {
                "username": row[0],
                "score": row[1]
            }
            for row in results
        ]
        return leaderboard_data
    except Exception as e:
        print(f"Error fetching leaderboard: {str(e)}", flush=True)
        return {"error": "Internal server error"}, 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.get('/ws/category-stats/{client_id}')
async def get_category_stats(client_id: str):
    print(f"Getting category stats for client {client_id}", flush=True)

    category_stats = {}
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            SELECT
                category,
                CASE
                    WHEN total_count = 0 THEN 0.0
                    ELSE (correct_count::float / total_count)
                END AS accuracy,
                avg_hints_used
            FROM metrics
            WHERE user_id = %s
        """
        cursor.execute(query, (client_id,))
        results = cursor.fetchall()
        print({"data": results}, flush=True)

        for row in results:
            category = row[0]
            accuracy = row[1]
            avg_hints_used = row[2]
            category_stats[category] = {
                "accuracy": accuracy,
                "avg_hints_used": avg_hints_used
            }
        return category_stats
    
    except Exception as e:
        print(f"Error fetching category stats: {str(e)}", flush=True)
        raise e
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()