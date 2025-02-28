from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
import uvicorn
from gamemaster import GameMaster

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
        # Initialize the game_master_number to 0, could cause issues with too many game masters
        self.game_master_number = 0
        
    def get_or_create_game_master(self, client_id: int, max_questions: int) -> int:
        if client_id not in self.game_masters:
            self.game_masters[client_id] = GameMaster(client_id, self.game_master_number, max_questions)
            print(f"Game Master {self.game_master_number} with client_id: {client_id} created")
            self.game_master_number += 1
        return client_id
    
    def end_game(self, client_id):
        gm = self.game_masters.get(client_id)
        gm.send_results()
        gm_id = gm.id
        del self.game_masters[client_id]

        print(f"Game Master {gm_id} with client_id: {client_id} deleted")
        return gm_id
