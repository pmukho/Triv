from pydantic import BaseModel
import datetime

class _GameBatchReqElem(BaseModel):
    category: str
    count: int

class GameBatchReq(BaseModel):
    user_id: str
    batch_size: int
    batch: list[_GameBatchReqElem]

class Question(BaseModel):
    id: str
    category: str
    hint1: str
    hint2: str
    hint3: str
    answer: str
    created_at: datetime.datetime
    usage_count: int
    downvotes: int

class GameBatchResp(BaseModel):
    batch: list[Question]

class DownvoteBatchReq(BaseModel):
    user_id: str
    batch: list[str]
