from typing import Optional

from src.database import functions
from src.database.functions import (
    PLAYERDATA_ENGINE,
    sqlalchemy_result,
    verify_token,
)
from src.database.models import Player, PredictionsFeedback
from src.utils import logging_helpers
from fastapi import APIRouter, HTTPException, Query, Request, status
from pydantic import BaseModel
from pydantic.fields import Field
from sqlalchemy import func, select
from sqlalchemy.dialects.mysql import Insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased
from sqlalchemy.sql.expression import Select, select


class Feedback(BaseModel):
    player_name: str
    vote: int
    prediction: str
    confidence: float = Field(default=0, ge=0, le=1)
    subject_id: int
    feedback_text: Optional[str] = None
    proposed_label: Optional[str] = None


router = APIRouter()


@router.get("/feedback/", tags=["Feedback"])
async def get_feedback(
    token: str,
    name: str,
    request: Request,
    row_count: Optional[int] = Query(100_000, ge=1, le=100_000),
    page: Optional[int] = Query(1, ge=1),
):
    """
    Get player feedback of a player
    """
    # verify token
    await verify_token(
        token,
        verification="verify_ban",
        route=logging_helpers.build_route_log_string(request),
    )

    name = await functions.to_jagex_name(name)

    # query
    table = PredictionsFeedback
    sql: Select = select(table)
    sql = sql.join(Player, PredictionsFeedback.voter_id == Player.id)
    sql = sql.where(Player.name == name)
    sql = sql.limit(row_count).offset(row_count * (page - 1))

    # execute query
    async with PLAYERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            data = await session.execute(sql)

    data = sqlalchemy_result(data)
    return data.rows2dict()


@router.get("/feedback/count", tags=["Feedback"])
async def get_feedback(name: str):
    """
    Get the calculated player feedback of a player
    """
    # query

    voter: Player = aliased(Player, name="voter")
    subject: Player = aliased(Player, name="subject")

    name = await functions.to_jagex_name(name)

    sql: Select = select(
        func.count(PredictionsFeedback.id),
        subject.confirmed_ban,
        subject.possible_ban,
        subject.confirmed_player,
    )
    sql = sql.join(voter, PredictionsFeedback.voter_id == voter.id)
    sql = sql.join(subject, PredictionsFeedback.subject_id == subject.id)
    sql = sql.where(voter.name == name)
    sql = sql.group_by(
        subject.confirmed_ban, subject.possible_ban, subject.confirmed_player
    )

    keys = ["count", "confirmed_ban", "possible_ban", "confirmed_player"]
    # execute query
    async with PLAYERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            data = await session.execute(sql)
            data = [{k: v for k, v in zip(keys, d)} for d in data]

    return data


@router.post("/feedback/", status_code=status.HTTP_201_CREATED, tags=["Feedback"])
async def post_feedback(feedback: Feedback):
    """
    Insert feedback into database
    """
    feedback: dict = feedback.dict()

    name = feedback.pop("player_name")
    name = await functions.to_jagex_name(name)

    sql_player: Select = select(Player)
    sql_player = sql_player.where(Player.name == name)
    sql_insert = Insert(PredictionsFeedback).prefix_with("ignore")

    async with PLAYERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            player = await session.execute(sql_player)
            player = sqlalchemy_result(player).rows2dict()

            if player == []:
                # create anonymous user if not exists
                if name.startswith("anonymoususer "):
                    await session.execute(Insert(Player).values(name=name))
                    player = await session.execute(sql_player)
                    player = sqlalchemy_result(player).rows2dict()
            # this could be an else statement
            try:
                feedback["voter_id"] = player[0]["id"]
            except IndexError:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Could not find voter in registry.",
                )

            sql_insert = sql_insert.values(feedback)
            await session.execute(sql_insert)

    return {"OK": "OK"}
