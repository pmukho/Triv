import pytest
import asyncio
from main import send_hints_timed, manager
from gamemaster import GameMaster

SAMPLE_QUESTIONS = [
    {
        "question": "What is the capital of France?",
        "answer": "Paris",
        "hint1": "It's also called the City of Light",
        "hint2": "Home of the Eiffel Tower",
        "hint3": "Famous for its museums",
        "id": "q1"
    },
    {
        "question": "5 + 7 = ?",
        "answer": "12",
        "hint1": "A dozen minus one",
        "hint2": "Even number",
        "hint3": "Basic arithmetic",
        "id": "q2"
    },
    {
        "question": "Who was the 16th President?",
        "answer": "Abe Lincoln",
        "hint1": "Hint 1",
        "hint2": "Hint 2",
        "hint3": "Hint 3",
        "id": "q3"
    }
]

# Fake async client to simulate httpx.AsyncClient behavior
class FakeAsyncClient:
    async def __aenter__(self):
        return self
    async def __aexit__(self, exc_type, exc_val, tb):
         pass
    async def post(self, url, json):
         class FakeResponse:
             status_code = 200
             def raise_for_status(self):
                 pass
             def json(self):
                 return {"batch": SAMPLE_QUESTIONS}
         return FakeResponse()

@pytest.mark.asyncio
async def test_load_questions_from_cache(monkeypatch):
    gm = GameMaster(1, "dummy")
    # Patch httpx.AsyncClient to use our fake client
    monkeypatch.setattr("gamemaster.httpx.AsyncClient", lambda: FakeAsyncClient())
    await gm.load_questions()
    # After loading, the questions should be set to SAMPLE_QUESTIONS
    assert hasattr(gm, "questions")
    assert gm.questions == SAMPLE_QUESTIONS

@pytest.mark.asyncio
async def test_check_answer_basic():
    gm = GameMaster(1, "dummy")
    gm.questions = SAMPLE_QUESTIONS
    gm.current_question = 0

    result, score, correct_answer, hints = await gm.check_answer("Paris")
    assert result is True

    gm.current_question = 0
    result, score, correct_answer, hints = await gm.check_answer("paris")
    assert result is True

    gm.current_question = 0
    result, score, correct_answer, hints = await gm.check_answer("London")
    assert result is False

@pytest.mark.asyncio
async def test_advanced_answer_check_single_token():
    gm = GameMaster(1, "dummy")
    gm.questions = SAMPLE_QUESTIONS
    gm.current_question = 2
    
    # Test with single token "Lincoln"
    result, score, correct_answer, hints = await gm.check_answer("Lincoln")
    assert result is True, "Single token 'Lincoln' should be accepted"
    
    # Test with single token "Abe"
    gm.current_question = 2
    result, score, correct_answer, hints = await gm.check_answer("Abe")
    assert result is True, "Single token 'Abe' should be accepted"

@pytest.mark.asyncio
async def test_advanced_answer_check_multiple_tokens():
    gm = GameMaster(1, "dummy")
    gm.questions = SAMPLE_QUESTIONS
    gm.current_question = 2
    
    # Test with multi-word answer that is close enough
    result, score, correct_answer, hints = await gm.check_answer("Abraham Lincoln")
    assert result is True, "Answer 'Abraham Lincoln' should be accepted as similar to 'Abe Lincoln'"
    
    # Test with a clearly incorrect multi-word answer
    gm.current_question = 0
    result, score, correct_answer, hints = await gm.check_answer("Abraham Obama")
    assert result is False, "Answer 'Abraham Obama' should not be accepted for 'Abe Lincoln'"

@pytest.mark.asyncio
async def test_check_answer_empty_and_no_questions():
    # Case 1: No questions loaded
    gm = GameMaster(1, "dummy")
    gm.questions = []
    gm.current_question = 0
    result, score, correct_answer, hints = await gm.check_answer("Anything")
    assert result is False, "With no questions, any answer should be rejected"
    assert score == 0
    assert correct_answer == ""
    assert hints == []

    # Case 2: Empty answer provided
    gm = GameMaster(1, "dummy")
    gm.questions = SAMPLE_QUESTIONS
    gm.current_question = 2
    result, score, correct_answer, hints = await gm.check_answer("")
    assert result is False, "An empty answer should be rejected"
    assert score == 0

@pytest.mark.asyncio
async def test_check_answer_with_punctuation_and_whitespace():
    # Test punctuation and extra whitespace in the answer do not affect correctness
    gm = GameMaster(1, "dummy")
    gm.questions = SAMPLE_QUESTIONS
    gm.current_question = 2
    result, score, correct_answer, hints = await gm.check_answer("  Abe,   Lincoln!  ")
    assert result is True, "Punctuation and extra whitespace should be normalized and accepted"

def test_downvote_triggers_hint():
    gm = GameMaster(1, "dummy")
    gm.questions = SAMPLE_QUESTIONS

    gm.current_question = 1
    returned_id = gm.downvote_question()
    
    # Verify that the returned ID matches the id from the first question
    assert returned_id == SAMPLE_QUESTIONS[0]["id"]
    # Check that the question's id was added to downvoted_questions
    assert SAMPLE_QUESTIONS[0]["id"] in gm.downvoted_questions

@pytest.mark.asyncio
async def test_send_hints_timed(monkeypatch):
    gm = GameMaster(1, "dummy")
    gm.questions = SAMPLE_QUESTIONS
    gm.current_question = 0

    # Override gamemaster api for test
    async def fake_get_hints():
         return ([gm.questions[0]["hint1"], gm.questions[0]["hint2"], gm.questions[0]["hint3"]], True)
    monkeypatch.setattr(gm, "get_hints", fake_get_hints)

    async def fast_sleep(duration):
         return
    monkeypatch.setattr(asyncio, "sleep", fast_sleep)

    messages_sent = []
    async def fake_send_message(client_id, message):
         messages_sent.append(message)
    monkeypatch.setattr(manager, "send_message", fake_send_message)
    
    # Call send_hints_timed with gm and a dummy client_id (1)
    await send_hints_timed(gm, 1)
    # Verify that three hint messages were sent
    assert len(messages_sent) == 3
    
    expected_hints = [
         gm.questions[0]["hint1"],
         gm.questions[0]["hint2"],
         gm.questions[0]["hint3"]
    ]
    for msg, expected in zip(messages_sent, expected_hints):
         assert msg.get("type") == "hint"
         assert msg.get("hint") == expected
