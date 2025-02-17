from fastapi import FastAPI, Request
from pydantic import BaseModel
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

print("Starting GameMaster API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["localhost", "localhost:3000", "localhost:8000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserInput(BaseModel):
    userInput: str

@app.post("/api/user-input")
async def receive_user_input(user_input: UserInput):
    # You can process the data here as needed
    print(f"Received user input: {user_input.userInput}")

    # Example response
    response = {
        "status": "success",
        "message": f"Received input: {user_input.userInput}"
    }
    return response

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
