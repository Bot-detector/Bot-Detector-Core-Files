from typing import Optional

from sqlalchemy.sql.expression import insert, select

from api.database.functions import verify_token, get_session, EngineType, sqlalchemy_result
from api.database.models import PredictionsFeedback, Player
from fastapi import APIRouter, status
from pydantic import BaseModel


class Feedback(BaseModel):
    player_name: str
    vote: int
    prediction: str
    confidence: float
    subject_id: int
    feedback_text: Optional[str] = None
    proposed_label: Optional[str] = None


router = APIRouter()

@router.get("/v1/feedback/", tags=["feedback"])
async def get(token:str):
    '''
    select data from database
    '''
    await verify_token(token, verifcation='ban')
    pass


@router.post("/v1/feedback/", status_code=status.HTTP_201_CREATED, tags=["feedback"])
async def post(feedback: Feedback, token:str):
    '''
    insert data into database
    '''
    await verify_token(token, verifcation='ban')
    feedback = feedback.dict()

    sql_player = select(Player)
    sql_player = sql_player.where(Player.name == feedback.pop('player_name'))

    sql_insert = insert(PredictionsFeedback).prefix_with('ignore')

    async with get_session(EngineType.PLAYERDATA) as session:
        player = session.execute(sql_player)
        player = sqlalchemy_result(player).rows2dict()

        feedback["voter_id"] = player[0]['id']
        sql_insert = sql_insert.values(feedback)
        print(sql_insert)
        await session.execute(sql_insert)
        
    return {"OK": "OK"}
