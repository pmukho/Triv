from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
import uvicorn
from gamemaster.gamemaster import GameMaster

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
    def get_or_create_game_master(self, client_id: str) -> GameMaster:
        if client_id not in self.game_masters:
            self.game_masters[client_id] = GameMaster(client_id)
        return self.game_masters[client_id]



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
