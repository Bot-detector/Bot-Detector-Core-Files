from fastapi.testclient import TestClient
from Config import app

client = TestClient(app)

def test_hiscore():
    response = client.get("/v1/hiscore")
    assert response.status_code == 200, f'invalid response {response.status_code }'
    assert response.json() == list, f'invalid response return type:'