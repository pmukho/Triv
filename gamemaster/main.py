from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from gmfactory import GmFactory
from typing import Optional
import json

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

class UserInput(BaseModel):
    userInput: str

class Answer(BaseModel):
    client_id: int
    answer: str


class ClientId(BaseModel):
    client_id: int

class ConnectionManager:
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
        for ws in self.active_wss.values():
            await ws.send_json(message)

    
class MaxQuestions(BaseModel):
    max_questions: int
    
gmFactory = GmFactory()
manager = ConnectionManager()

hint_tasks = {}
@app.websocket("/ws/quiz/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
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
                task = asyncio.create_task(send_hints_timed(gm, client_id))
                hint_tasks[client_id] = task
                
                await manager.send_message(client_id, {
                    "type": "game_status",
                    "status": "Started question"
                })
            elif msg_type == "submit_answer":
                user_answer = payload.get("answer", "")
                is_correct, score = await gm.check_answer(user_answer)
                await manager.send_message(client_id, {
                    "type": "answer_result",
                    "correct": is_correct,
                    "score": score
                })
                # Cancel any timer
                hint_tasks[client_id].cancel()
                task = asyncio.create_task(send_hints_timed(gm, client_id))
                hint_tasks[client_id] = task
            elif msg_type == "end_game":
                gm_id = gmFactory.end_game(client_id)
                if hint_tasks.get(client_id):
                    hint_tasks[client_id].cancel()
                    hint_tasks.pop(client_id, None)

                await manager.send_message(client_id, {
                    "type": "game_status",
                    "status": "Game ended",
                    "gm_id": gm_id
                })

    # Handle disconnect and other errors
    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        print(f"Error in WebSocket communication with client {client_id}: {e}")
        await websocket.close()

async def send_hints_timed(game_master, client_id: int):
    try:
        # Fetch hints
        hints, has_question = await game_master.get_hints()
        if not has_question or len(hints) < 3:
            print("Not enough hints available.")
            return

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

