import pytest
from main import ConnectionManager

# Dummy WebSocket
class DummyWebSocket:
    def __init__(self):
        self.sent_messages = []
        self.closed = False

    async def accept(self):
        pass

    async def send_json(self, message: dict):
        self.sent_messages.append(message)

    async def close(self):
        self.closed = True

@pytest.fixture(autouse=True)
def manager():
    # Create a new ConnectionManager instance for each test
    manager = ConnectionManager()
    yield manager
    # Teardown: clear active connections after each test
    manager.active_connections.clear()

@pytest.mark.asyncio
async def test_connect_adds_connection(manager):
    client_id = 1
    ws = DummyWebSocket()
    await manager.connect(client_id, ws)
    # Verify that the websocket is added to active connections
    assert client_id in manager.active_connections
    assert manager.active_connections[client_id] is ws
    # Clean up by disconnecting the client
    manager.disconnect(client_id)
    assert client_id not in manager.active_connections

@pytest.mark.asyncio
async def test_disconnect_removes_connection(manager):
    client_id = 1
    ws = DummyWebSocket()
    # Add the connection then remove it
    await manager.connect(client_id, ws)
    assert client_id in manager.active_connections
    manager.disconnect(client_id)
    # After disconnect, the websocket should be removed
    assert client_id not in manager.active_connections

@pytest.mark.asyncio
async def test_send_personal_message(manager):
    client_id = 1
    ws = DummyWebSocket()
    await manager.connect(client_id, ws)
    # Send a personal message to the connected websocket
    message = {"text": "Hello Player1"}
    await manager.send_message(client_id, message)
    # Verify that the message was sent
    assert message in ws.sent_messages
