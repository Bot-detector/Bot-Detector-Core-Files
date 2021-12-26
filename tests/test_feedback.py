import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from api import app
from api.Config import token
from fastapi.testclient import TestClient

client = TestClient(app.app)

"""
  Feedback get routes
"""

@pytest.mark.filterwarnings('ignore::DeprecationWarning')
def test_get_feedback():
  
    test_case = (
      (8, 1, 1,'Real_Player',1,'testing', 200), # correct
      ('shoe', 1, 1,'Real_Player',1,'testing', 422), # invalid voter id type
      (8, 'shoe', 1,'Real_Playerr',1,'testing', 422), # invalid subject id type
      (8, 1, 'shoe','Real_Player',1,'testing', 422), # invalid vote type
      (8, 1, 1000000,'Real_Player',1,'testing', 200), # invalid vote value
      (8, 1, -1000000,'Real_Player',1,'testing', 200), # invalid vote value
      (8, 1, 1, 100, 1,'testing', 200), # invalid prediction value
      (8, 1, 1, 'Real_Player', 'very_confident','testing', 422), # invalid confidence type
      (8, 1, 1, 'Real_Player', 0.5,'testing', 200), # valid confidence type
      (8, 1, 1, 'Real_Player', 1000,'testing', 200), # invalid confidence range
    )
    
    for voter_id, subject_id, vote, prediction, confidence, feedback_text, response_code in test_case:
        route_attempt = f'/v1/feedback/?token={token}&voter_id={voter_id}&subject_id={subject_id}&vote={vote}&prediction={prediction}&confidence={confidence}&feedback_text={feedback_text}'
        response = client.get(route_attempt)
        assert response.status_code == response_code, f'{route_attempt} | Invalid response {response.status_code}'
        if response.status_code == 200:
            assert isinstance(response.json(), list), f'invalid response return type: {type(response.json())}'

if __name__ == "__main__":
    test_get_feedback()
