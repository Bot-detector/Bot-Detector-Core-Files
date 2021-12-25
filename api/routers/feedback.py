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
    subject_id: int # are they sending a subject id?
    feedback_text: Optional[str] = None
    proposed_label: Optional[str] = None


router = APIRouter()


@router.get("/v1/feedback/", tags=["Feedback"])
async def get_feedback(token: str):
    '''
    Work in progress.
    Get player feedback of a player
    '''
    await verify_token(token, verification='verify_ban', route='[GET]/v1/feedback')
    pass


@router.post("/v1/feedback/", status_code=status.HTTP_201_CREATED, tags=["Feedback"])
async def post(feedback: Feedback):
    '''
        insert feedback into database
    '''
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
