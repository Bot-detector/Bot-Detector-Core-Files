from datetime import datetime
from typing import Optional

from api.database.functions import (
    EngineType,
    get_session,
    sqlalchemy_result,
    verify_token,
)
from api.database.models import Player, PredictionsFeedback
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel
from pydantic.fields import Field
from sqlalchemy.sql.expression import insert, select


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
    since_id: Optional[int] = None,
    since_date: Optional[datetime] = None,
    voter_id: Optional[int] = Query(None, ge=0),
    subject_id: Optional[int] = Query(None, ge=0),
    vote: Optional[int] = Query(None, ge=-1, le=1),
    prediction: Optional[str] = None,
    confidence: Optional[float] = Query(None, ge=0, le=1),
    proposed_label: Optional[str] = None,
    feedback_text: Optional[str] = None,
    has_text: Optional[bool] = None,
    row_count: Optional[int] = Query(100_000, ge=1, le=100_000),
    page: Optional[int] = Query(1, ge=1),
):
    """
    Get player feedback of a player
    """
    # verify token
    await verify_token(token, verification="verify_ban", route="[GET]/v1/feedback")

    if (
        None
        == voter_id
        == subject_id
        == vote
        == prediction
        == confidence
        == proposed_label
        == feedback_text
        == since_date
        == since_id
        == has_text
    ):
        raise HTTPException(status_code=404, detail="No param given")

    # query
    table = PredictionsFeedback
    sql = select(table)

    # filters
    if not since_id == None:
        sql = sql.where(table.id > since_id)
    if not since_date == None:
        sql = sql.where(table.ts > since_date)
    if not voter_id is None:
        sql = sql.where(table.voter_id == voter_id)
    if not subject_id is None:
        sql = sql.where(table.subject_id == subject_id)
    if not vote is None:
        sql = sql.where(table.vote == vote)
    if not prediction is None:
        sql = sql.where(table.prediction == prediction)
    if not confidence is None:
        sql = sql.where(table.confidence == confidence)
    if not proposed_label is None:
        sql = sql.where(table.proposed_label == proposed_label)
    if not feedback_text is None:
        sql = sql.where(table.feedback_text == feedback_text)
    if not has_text == None:
        sql = sql.where(table.feedback_text != None)

    sql = sql.limit(row_count).offset(row_count * (page - 1))

    # execute query
    async with get_session(EngineType.PLAYERDATA) as session:
        data = await session.execute(sql)

    data = sqlalchemy_result(data)
    return data.rows2dict()


@router.post("/v1/feedback/", status_code=status.HTTP_201_CREATED, tags=["Feedback"])
async def post_feedback(feedback: Feedback):
    """
    Insert feedback into database
    """
    feedback = feedback.dict()

    sql_player = select(Player)
    sql_player = sql_player.where(Player.name == feedback.pop("player_name"))
    sql_insert = insert(PredictionsFeedback).prefix_with("ignore")

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
