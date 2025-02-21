from fastapi import FastAPI, Request
from pydantic import BaseModel
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from gmfactory import GmFactory 
class UserInput(BaseModel):
    userInput: str

class Answer(BaseModel):
    client_id: int
    answer: str

class ClientId(BaseModel):
    client_id: int

class GameMasterCreation(BaseModel):
    gm_id: int
    status: str

class Hints(BaseModel):
    hints: list[str]
    hints_complete: bool

class AnswerResponse(BaseModel):
    correct: bool
    score: int

class UserInputRespose(BaseModel):
    status: str
    message: str

gmFactory = GmFactory()

tags_metadata = [
    {
        "name": "start-game",
        "description": "Start a new game, returns a Game Master ID so the client can route",
    },
    {
        "name": "request-hints",
        "description": "Request hints for the current question.\n Hint completion status is vestigial, will be adapted in future versions\
            \n **TODO**: Grab hints from cache instead of dummy response. Have hints sent one at a time instead of all at once for security reasons",
    },
    {
        "name": "submit-answer",
        "description": "Submit an answer to the current question, returns whether the answer was correct and the current score",
    },
    {
        "name": "user-input",
        "description": "Receive user input, **This is a testing function which will be removed in future versions**",
    },
]

app = FastAPI(openapi_tags=tags_metadata)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost"],
    allow_methods=["POST"],
    allow_headers=["*"],
)


@app.post("/api/start-game", tags=["start-game"])
async def start_game(client: ClientId) -> GameMasterCreation:
    gm_id = gmFactory.game_masters[gmFactory.get_or_create_game_master(client.client_id)]
    return GameMasterCreation(gm_id=gm_id, status="Game Master created")

@app.post("/api/request-hints", tags=["request-hints"])
async def request_hints(client: ClientId) -> Hints:
    gm = gmFactory.game_masters[gmFactory.get_or_create_game_master(client.client_id)]
    hints, hints_complete = await gm.get_hints()
    return Hints(hints=hints, hints_complete=hints_complete)

@app.post("/api/submit-answer", tags=["submit-answer"])
async def submit_answer(answer: Answer) -> AnswerResponse:
    print(f"Received answer: {answer.answer} from client: {answer.client_id}")
    gm = gmFactory.game_masters[gmFactory.get_or_create_game_master(answer.client_id)]
    is_correct,score = await gm.check_answer(answer.answer)
    return AnswerResponse(correct=is_correct, score=score)

# @app.post("/{client_id}/downvote")
# async def downvote_question(client_id: str, downvote: DownVote):
#     gm = get_or_create_game_master(client_id)
#     await gm.downvote_question()
#     return {"status": "Downvote recorded"}


# @app.post("/{client_id}/data")
# async def send_data(client_id: str, data: Data):
#     # Implement data handling logic
#     return {"status": "Data sent successfully"}

@app.post("/api/user-input", tags=["user-input"])
async def receive_user_input(user_input: UserInput) -> UserInputRespose:
    # You can process the data here as needed
    print(f"Received user input: {user_input.userInput}")
    # Example response
    response = {
        "status": "success",
        "message": f"Received input: {user_input.userInput}"
    }
    return UserInputRespose(**response)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
