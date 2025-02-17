from fastapi import FastAPI, Request
from pydantic import BaseModel
import uvicorn
from fastapi.middleware.cors import CORSMiddleware


class GameMaster:
    def __init__(self, client_id):
        self.client_id = client_id
        self.current_question = None
        self.score = 0
   