from typing import Optional

from sqlalchemy.dialects.mysql.types import TIMESTAMP
from sqlalchemy.sql.sqltypes import Text

from api.database.functions import execute_sql, list_to_string, verify_token
from fastapi import APIRouter, status
from pydantic import BaseModel


from api.database.database import EngineType, get_session
from api.database.functions import sqlalchemy_result, verify_token
from api.database.models import (PredictionsFeedback)
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy.sql.expression import insert, select


class Feedback(BaseModel):
    player_name: str
    vote: int
    prediction: str
    confidence: float
    subject_id: int
    feedback_text: Optional[str] = None
    proposed_label: Optional[str] = None


router = APIRouter()


@router.get("/v1/feedback/", tags=["Feedback"])
async def get_feedback(
    token: str,
    voter_id: Optional[int] = None,
    subject_id: Optional[int] = None,
    prediction: Optional[str] = None,
    confidence: Optional[float] = None,
    vote: Optional[int] = None,
    feedback_text: Optional[str] = None,
    ):
    
    '''
        Get player feedback of a player
    '''
    await verify_token(token, verification='verify_ban', route='[GET]/v1/feedback')

    # query
    sql = select(PredictionsFeedback)

    # filters
    if voter_id == subject_id == prediction == confidence == vote == feedback_text == None:
        return {'None':'Please enter in one field for filtering.'}
    
    if not voter_id == None:
        sql = sql.where(PredictionsFeedback.voter_id == voter_id)
        
    if not subject_id == None:
        sql = sql.where(PredictionsFeedback.subject_id == subject_id)
        
    if not prediction == None:
        sql = sql.where(PredictionsFeedback.prediction == prediction)
        
    if not confidence == None:
        sql = sql.where(PredictionsFeedback.confidence == confidence)
        
    if not vote == None:
        sql = sql.where(PredictionsFeedback.vote == vote)
        
    if not feedback_text == None:
        sql = sql.where(PredictionsFeedback.feedback_text == feedback_text)

    async with get_session(EngineType.PLAYERDATA) as session:
        data = await session.execute(sql)

    data = sqlalchemy_result(data)
    return data.rows2dict()


@router.post("/v1/feedback/", status_code=status.HTTP_201_CREATED, tags=["Feedback"])
async def insert_feedback(feedback: Feedback, token: str):
    '''
        Insert prediction feedback into database.
    '''
    await verify_token(token, verification='verify_ban', route='[POST]/v1/feedback')
    feedback_params = feedback.dict()

    voter_data = await execute_sql(sql=f"select * from Players where name = :player_name", param={"player_name": feedback_params.pop("player_name")})
    voter_data = voter_data.rows2dict()[0]

    feedback_params["voter_id"] = voter_data.get("id")
    exclude = ["player_name"]

    columns = [k for k, v in feedback_params.items(
    ) if v is not None and k not in exclude]
    columns = list_to_string(columns)

    values = [f':{k}' for k, v in feedback_params.items(
    ) if v is not None and k not in exclude]
    values = list_to_string(values)

    sql = (f'''
        insert ignore into PredictionsFeedback ({columns})
        values ({values}) 
    ''')

    await execute_sql(sql, param=feedback_params)

    return {"OK": "OK"}
