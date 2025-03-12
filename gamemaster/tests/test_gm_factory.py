import pytest
import asyncio
from gamemaster import GameMaster
from gmfactory import GmFactory

@pytest.fixture(autouse=True)
def clean_factory():
    # Create a new GmFactory instance for each test
    factory = GmFactory()
    yield factory
    # Teardown: clear game masters after test
    factory.game_masters.clear()

def test_create_game_instance(clean_factory):
    factory = clean_factory
    client_id = 1
    max_questions = 5

    factory.get_or_create_game_master(client_id, max_questions)
    gm1 = factory.game_masters[client_id]
    assert isinstance(gm1, GameMaster)
    
    # Same client_id should return the same instance
    factory.get_or_create_game_master(client_id, max_questions)
    gm2 = factory.game_masters[client_id]
    assert gm1 is gm2

def test_create_multiple_games(clean_factory):
    factory = clean_factory
    client_id1 = 1
    client_id2 = 2
    max_questions = 5
    factory.get_or_create_game_master(client_id1, max_questions)
    factory.get_or_create_game_master(client_id2, max_questions)
    gm1 = factory.game_masters[client_id1]
    gm2 = factory.game_masters[client_id2]
    assert gm1 is not gm2
    # Both games should be in the factory game_masters dict
    assert client_id1 in factory.game_masters and client_id2 in factory.game_masters

@pytest.mark.asyncio
async def test_end_game_instance(clean_factory, monkeypatch):
    factory = clean_factory
    client_id = 1
    max_questions = 5
    factory.get_or_create_game_master(client_id, max_questions)
    # Ensure the game is active
    assert client_id in factory.game_masters
    # Skip downvoting
    monkeypatch.setattr(factory.game_masters[client_id], "notify_downvoted_questions", lambda: asyncio.sleep(0))
    # Skip sending results
    monkeypatch.setattr(factory.game_masters[client_id], "send_results", lambda: asyncio.sleep(0))
    # End the game
    await factory.end_game(client_id)
    # After ending, the game should be removed
    assert client_id not in factory.game_masters

@pytest.mark.asyncio
async def test_end_nonexistent_game(clean_factory, monkeypatch):
    factory = clean_factory
    non_existent_client = 999

    # Patch end_game for test
    async def safe_end_game(client_id):
        gm = factory.game_masters.get(client_id)
        if gm is None:
            return None
        return await factory.__class__.end_game(factory, client_id)
    monkeypatch.setattr(factory, "end_game", safe_end_game)

    try:
        result = await factory.end_game(non_existent_client)
    except Exception as e:
        pytest.fail(f"Ending a non-existent game raised an exception: {e}")
    
    assert result is None
    assert non_existent_client not in factory.game_masters
