from fastapi import FastAPI, Request
from pydantic import BaseModel
import uvicorn
from fastapi.middleware.cors import CORSMiddleware


class GameMaster:
    def __init__(self, client_id, gm_instance_id):
        self.client_id = client_id
        self.current_question = 0
        self.score = 0
        self.id = gm_instance_id
    async def get_hints(self):
        # Implement logic to get the next hints
        print(f"Game Master {self.client_id+self.current_question} getting hints and sending them")
        return [f"What is {self.client_id+self.current_question}*2?",f"What is {self.client_id+self.current_question}+ {self.client_id+self.current_question}?",f"The answer is {(self.client_id+self.current_question)*2}"],True
    async def check_answer(self, answer):
        # Implement logic to check the answer
        if answer.lower() == f"{(self.client_id+self.current_question)*2}".lower():
            self.score += 1
            self.current_question += 1
            return True, self.score
        else:
            self.current_question += 1
            return False, self.score
    async def downvote_question(self):
        # Implement logic to downvote the current question
        pass
    async def send_hints(self, hints):
        # Implement logic to send hints
        pass
    async def send_data(self, metrics_data):
        # Implement logic to send data
        pass
