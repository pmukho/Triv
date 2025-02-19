from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
import pytest

from .main import app

# client = TestClient(app)

# def test_post_questions():
#     response = client.post("/questions", json={"article_names": ["Pablo Escobar", 'Abraham_Lincoln']})
#     print(response.json())
#     assert response.status_code == 200

# if __name__ == "__main__":
#     test_post_questions()
    
@pytest.mark.anyio
async def test_post_questions():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/questions", json={"article_names": ["Pablo Escobar", 'Abraham_Lincoln']})
    assert response.status_code == 200
    print(response.json())