import pytest
import json
from fastapi.testclient import TestClient
import sys
import os


from main import app, get_db_connection
client = TestClient(app)

def mock_get_db_connection():
    class MockCursor:
        def execute(self, query, params):
            if "WHERE uqs.question_id IS NULL" in query:
                self.result = [
                    (1, "What is AI?", "Science", "2025-01-01"),
                    (2, "Who invented Python?", "Technology", "2025-01-02"),
                ]
            else:
                self.result = []
        
        def fetchall(self):
            return self.result
        
        def close(self):
            pass
    
    class MockConnection:
        def cursor(self):
            return MockCursor()
        
        def close(self):
            pass

    return MockConnection()

@pytest.fixture(autouse=True)
def patch_db(monkeypatch):
    monkeypatch.setattr("main.get_db_connection", mock_get_db_connection)

def test_getbatch_success():
    payload = {
        "user_id": "123",
        "batch_size": 2,
        "batch": [{"category": "Science", "count": 1}, {"category": "Technology", "count": 1}]
    }
    response = client.post("/getbatch/", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert len(data) == 2
    assert data[0][1] == "What is AI?"
    assert data[1][1] == "Who invented Python?"


def test_getbatch_invalid_request():
    payload = {
        "batch_size": 2,
        "batch": [{"category": "Science", "count": 1}]
    }
    response = client.post("/getbatch/", json=payload)
    assert response.status_code == 422

def test_getbatch_db_failure(monkeypatch):
    def mock_db_failure():
        raise Exception("Database connection error")

    monkeypatch.setattr("main.get_db_connection", mock_db_failure)
    
    payload = {
        "user_id": "123",
        "batch_size": 2,
        "batch": [{"category": "Science", "count": 1}]
    }
    response = client.post("/getbatch/", json=payload)
    assert response.status_code == 200
    assert response.json() == []