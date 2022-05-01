
from typing import Optional

from api.database.functions import (EngineType, get_session, sqlalchemy_result,
                                    verify_token)
from api.database.models import Player, PredictionsFeedback
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel
from pydantic.fields import Field
from sqlalchemy import func, select
from sqlalchemy.dialects.mysql import Insert
from sqlalchemy.orm import aliased
from sqlalchemy.sql.expression import Select, select


class Feedback(BaseModel):
    player_name: str
    vote: int
    prediction: str
    confidence: float = Field(None, ge=0, le=1)
    subject_id: int
    feedback_text: Optional[str] = None
    proposed_label: Optional[str] = None


router = APIRouter()


@router.get("/v1/feedback/", tags=["Feedback"])
async def get_feedback(
    token: str,
    name: str,
    row_count: Optional[int] = Query(100_000, ge=1, le=100_000),
    page: Optional[int] = Query(1, ge=1),
):
    """
    Get player feedback of a player
    """
    # verify token
    await verify_token(token, verification="verify_ban", route="[GET]/v1/feedback")


    # query
    table = PredictionsFeedback
    sql:Select = select(table)
    sql = sql.join(Player, PredictionsFeedback.voter_id == Player.id)
    sql = sql.where(Player.name == name)
    sql = sql.limit(row_count).offset(row_count * (page - 1))

    # execute query
    async with get_session(EngineType.PLAYERDATA) as session:
        data = await session.execute(sql)

    data = sqlalchemy_result(data)
    return data.rows2dict()

@router.get("/v1/feedback/count", tags=["Feedback"])
async def get_feedback(
    name: str
):
    """
    Get the calculated player feedback of a player
    """
    # query
    
    voter:Player = aliased(Player, name="voter")
    subject:Player = aliased(Player, name="subject")

    sql:Select = select(
        func.count(PredictionsFeedback.id),
        subject.confirmed_ban,
        subject.possible_ban,
        subject.confirmed_player
    )
    sql = sql.join(voter, PredictionsFeedback.voter_id == voter.id)
    sql = sql.join(subject, PredictionsFeedback.subject_id == subject.id)
    sql = sql.where(voter.name == name)
    sql = sql.group_by(
        subject.confirmed_ban,
        subject.possible_ban,
        subject.confirmed_player
    )

    keys = ["count","confirmed_ban","possible_ban","confirmed_player"]
    # execute query
    async with get_session(EngineType.PLAYERDATA) as session:
        data = await session.execute(sql)
        data = [{k:v for k,v in zip(keys,d)} for d in data]

    return data

@router.post("/v1/feedback/", status_code=status.HTTP_201_CREATED, tags=["Feedback"])
async def post_feedback(feedback: Feedback):
    """
    Insert feedback into database
    """
    feedback = feedback.dict()

    sql_player:Select = select(Player)
    sql_player = sql_player.where(Player.name == feedback.pop("player_name"))
    sql_insert = Insert(PredictionsFeedback).prefix_with("ignore")

    async with get_session(EngineType.PLAYERDATA) as session:
        player = await session.execute(sql_player)
        player = sqlalchemy_result(player).rows2dict()

        try:
            feedback["voter_id"] = player[0]["id"]
        except IndexError:
            raise HTTPException(
                status_code=500, detail="Could not find voter in registry."
            )

        sql_insert = sql_insert.values(feedback)
        await session.execute(sql_insert)
        await session.commit()

    return {"OK": "OK"}
