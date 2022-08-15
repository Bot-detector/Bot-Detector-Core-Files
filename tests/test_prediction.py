import os
import sys
from typing import Union

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api import app
from fastapi.testclient import TestClient
from pydantic import BaseModel

client = TestClient(app.app)


def test_prediction():
    url = "/v1/prediction/"
    breakdown_param = [
        {
            "name": "3BA604236FB0319D5937E31388B0C64C"
        },
                {
            "name": "3BA604236FB0319D5937E31388B0C64C",
            "breakdown": True
        },
        {
            "name": "3BA604236FB0319D5937E31388B0C64C",
            "breakdown": False
        }
    ]
    for param in breakdown_param:
        response = client.get(url, params=param)
        check_response(response, param, 200)
        prediction = parse_response(response)
        error = f"Expected prediction_confidence is not None, {param=}"
        assert prediction.prediction_confidence is not None, error
        error = f"Expected prediction_breakdown is not None, {param=}"
        assert prediction.predictions_breakdown is not None, error

    no_breakdown_param = [
        {
            "name": "2C09003E9EA22E5F245023B5555C0AD9"
        },
        {
            "name": "2C09003E9EA22E5F245023B5555C0AD9",
            "breakdown": False
        }
    ]
    for param in no_breakdown_param:
        response = client.get(url, params=param)
        check_response(response, param, 200)
        prediction = parse_response(response)
        error = f"Expected prediction_confidence is None, {param=}"
        assert prediction.prediction_confidence is None, error
        error = f"Expected prediction_breakdown is None, {param=}"
        assert prediction.predictions_breakdown is None, error

    param = {
        "name": "2C09003E9EA22E5F245023B5555C0AD9",
        "breakdown": True
    }
    response = client.get(url, params=param)
    check_response(response, param, 200)
    prediction = parse_response(response)
    error = f"Expected prediction_confidence is None, {param=}"
    assert prediction.prediction_confidence is None, error
    error = f"Expected prediction_breakdown is not None, {param=}"
    assert prediction.predictions_breakdown is not None, error

    param = {
        "name": None
    }
    response = client.get(url, params=param)
    check_response(response, param, 422)
