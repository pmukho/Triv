from fastapi import FastAPI, Request
from pydantic import BaseModel
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from gmfactory import GmFactory 
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserInput(BaseModel):
    userInput: str

class Answer(BaseModel):
    client_id: int
    answer: str


class ClientId(BaseModel):
    client_id: int
gmFactory = GmFactory()


@ app.post("/api/start-game")
async def start_game(client: ClientId):
    gm_id = gmFactory.game_masters[gmFactory.get_or_create_game_master(client.client_id)]
    return {"status": "Game Master created", "gm_id": gm_id}
@app.post("/api/request-hints")
async def request_hints(client: ClientId):
    gm = gmFactory.game_masters[gmFactory.get_or_create_game_master(client.client_id)]
    hints,hints_complete = await gm.get_hints()
    return {"hints": hints, "hints_complete": hints_complete}

@app.post("/api/submit-answer")
async def submit_answer(answer: Answer):
    print(f"Received answer: {answer.answer} from client: {answer.client_id}")
    gm = gmFactory.game_masters[gmFactory.get_or_create_game_master(answer.client_id)]
    is_correct,score = await gm.check_answer(answer.answer)
    return {"correct": is_correct, "score": score}

# @app.post("/{client_id}/downvote")
# async def downvote_question(client_id: str, downvote: DownVote):
#     gm = get_or_create_game_master(client_id)
#     await gm.downvote_question()
#     return {"status": "Downvote recorded"}


# @app.post("/{client_id}/data")
# async def send_data(client_id: str, data: Data):
#     # Implement data handling logic
#     return {"status": "Data sent successfully"}

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
