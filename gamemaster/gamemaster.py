from fastapi import FastAPI, Request
from pydantic import BaseModel
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import httpx

CACHE_SERVICE_URL = "http://cache:8000"

class GameMaster:
    def __init__(self, client_id, gm_instance_id):
        self.client_id = client_id
        self.current_question = 0
        self.score = 0
        self.id = gm_instance_id
        self.questions = []

    async def load_questions(self):
        # Load batch from cache
        if self.questions:
            return

        # Prepare payload
        payload = {
            "user_id": str(self.client_id),
            "batch_size": 2,
            "batch": [{"category": "CAT1", "count": 3}, {"category": "CAT2", "count": 3}]
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(f"{CACHE_SERVICE_URL}/getbatch/", json=payload)
                response.raise_for_status()
                self.questions = response.json()["batch"]
                print("Loaded questions:", self.questions)
            except Exception as e:
                print("Error loading questions:", e)
                self.questions = []

    async def get_hints(self):
        # Implement logic to get the next hints
        await self.load_questions()
        if self.current_question < len(self.questions):
            q = self.questions[self.current_question]
            hints = [q["hint1"], q["hint2"], q["hint3"]]
            return hints, True
        else:
            return [], False
    
    async def check_answer(self, answer):
        # Implement logic to check the answer
        await self.load_questions()

        if self.current_question < len(self.questions):
            q = self.questions[self.current_question]
            correct_answer = q["answer"]

            if answer.lower() == correct_answer.lower():
                self.score += 1
                result = True
            else:
                result = False

            self.current_question += 1
            return result, self.score
        else:
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
