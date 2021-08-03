from fastapi.testclient import TestClient
from Config import app

client = TestClient(app)

def test_hiscore():
    response = client.get("/hiscore")
    assert response.status_code == 200
    assert response.json() == list