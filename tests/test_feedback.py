import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from api import app
from fastapi.testclient import TestClient

client = TestClient(app.app)

"""
  Feedback get routes
"""

#TODO: test feedback
@pytest.mark.filterwarnings('ignore::DeprecationWarning')
def test_get_feedback():
  """
    test feedback count
  """
  url = f'/v1/feedback/count?name=extreme4all'
  response = client.get(url)
  assert response.status_code == 200, f'Invalid response {response.status_code}, {response.text}'
  assert isinstance(response.json(), list), f'invalid response return type: {type(response.json())}'


if __name__ == "__main__":
    '''get tests'''
    test_get_feedback()
    
    '''post tests'''
    # test_post_feedback()
