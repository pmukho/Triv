from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
import uvicorn
from gamemaster import GameMaster

app = FastAPI()
class Question(BaseModel):
    id: str
    text: str

class Answer(BaseModel):
    question_id: str
    ans: str

class DownVote(BaseModel):
    question_id: str
    down_vote: bool

class Hint(BaseModel):
    question_id: str
    hints: list[str]

class Data(BaseModel):
    client_id: str
    Metrics: dict

# GmFacroty class to manage GameMaster instances
class GmFactory:
    def __init__(self):
        self.game_masters = {}
        self.app = app
        # Initialize the game_master_number to 0, could cause issues with too many game masters
        self.game_master_number = 0
    def get_or_create_game_master(self, client_id: int) -> int:
        if client_id not in self.game_masters:
            self.game_masters[client_id] = GameMaster(client_id, self.game_master_number)
            self.game_master_number += 1
            print(f"Game Master with client_id: {client_id} created")
        return client_id



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
