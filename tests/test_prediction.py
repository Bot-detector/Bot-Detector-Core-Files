import os
import sys
from typing import Union

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pydantic import BaseModel


class Prediction(BaseModel):
    player_id: int
    player_name: str
    prediction_label: str
    prediction_confidence: Union[None, float]
    created: str
    predictions_breakdown: Union[None, dict]


def check_response(response, param, code):
    error = (
        f"Invalid response, Received: {response.status_code}, expected 200, {param=}"
    )
    assert response.status_code == code, error


def parse_response(response):
    response = response.json()
    try:
        prediction = Prediction(**response)
        return prediction
    except Exception as e:
        assert False, e


def test_prediction(test_client):
    url = "/v1/prediction/"
    breakdown_param = [
        {"name": "3BA604236FB0319D5937E31388B0C64C"},
        {"name": "3BA604236FB0319D5937E31388B0C64C", "breakdown": True},
        {"name": "3BA604236FB0319D5937E31388B0C64C", "breakdown": False},
    ]
    for param in breakdown_param:
        response = test_client.get(url, params=param)
        check_response(response, param, 200)
        prediction = parse_response(response)
        error = f"Expected prediction_confidence is not None, {param=}"
        assert prediction.prediction_confidence is not None, error
        error = f"Expected prediction_breakdown is not None, {param=}"
        assert prediction.predictions_breakdown is not None, error

    no_breakdown_param = [
        {"name": "2C09003E9EA22E5F245023B5555C0AD9"},
        {"name": "2C09003E9EA22E5F245023B5555C0AD9", "breakdown": False},
    ]
    for param in no_breakdown_param:
        response = test_client.get(url, params=param)
        check_response(response, param, 200)
        prediction = parse_response(response)
        error = f"Expected prediction_confidence is None, {param=}"
        assert prediction.prediction_confidence is None, error
        error = f"Expected prediction_breakdown is None, {param=}"
        assert prediction.predictions_breakdown is None, error

    param = {"name": "2C09003E9EA22E5F245023B5555C0AD9", "breakdown": True}
    response = test_client.get(url, params=param)
    check_response(response, param, 200)
    prediction = parse_response(response)
    error = f"Expected prediction_confidence is None, {param=}"
    assert prediction.prediction_confidence is None, error
    error = f"Expected prediction_breakdown is not None, {param=}"
    assert prediction.predictions_breakdown is not None, error

    param = {"name": None}
    response = test_client.get(url, params=param)
    check_response(response, param, 422)
