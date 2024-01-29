from operator import or_
from typing import List, Optional

from src.database import functions
from src.database.functions import (
    PLAYERDATA_ENGINE,
    list_to_string,
    sqlalchemy_result,
    verify_token,
)
from src.database.models import Player, PlayerHiscoreDataLatest
from src.database.models import Prediction as dbPrediction
from src.utils import logging_helpers
from fastapi import APIRouter, HTTPException, Query, Request, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import Select, select, text
from sqlalchemy.sql.functions import func

router = APIRouter()


class Prediction(BaseModel):
    name: str
    Prediction: str
    id: int
    created: str
    Predicted_confidence: float
    Real_Player: Optional[float] = 0
    PVM_Melee_bot: Optional[float] = 0
    Smithing_bot: Optional[float] = 0
    Magic_bot: Optional[float] = 0
    Fishing_bot: Optional[float] = 0
    Mining_bot: Optional[float] = 0
    Crafting_bot: Optional[float] = 0
    PVM_Ranged_Magic_bot: Optional[float] = 0
    PVM_Ranged_bot: Optional[float] = 0
    Hunter_bot: Optional[float] = 0
    Fletching_bot: Optional[float] = 0
    Clue_Scroll_bot: Optional[float] = 0
    LMS_bot: Optional[float] = 0
    Agility_bot: Optional[float] = 0
    Wintertodt_bot: Optional[float] = 0
    Runecrafting_bot: Optional[float] = 0
    Zalcano_bot: Optional[float] = 0
    Woodcutting_bot: Optional[float] = 0
    Thieving_bot: Optional[float] = 0
    Soul_Wars_bot: Optional[float] = 0
    Cooking_bot: Optional[float] = 0
    Vorkath_bot: Optional[float] = 0
    Barrows_bot: Optional[float] = 0
    Herblore_bot: Optional[float] = 0
    Zulrah_bot: Optional[float] = 0
    Unknown_bot: Optional[float] = 0
    Gauntlet_bot: Optional[float] = 0
    Nex_bot: Optional[float] = 0


@router.get("/prediction", tags=["Prediction"])
async def get_account_prediction_result(name: str, breakdown: Optional[bool] = False):
    """
    Parameters:
        name: The name of the player to get the prediction for
        breakdown: If True, always return breakdown, even if the prediction is Stats_Too_Low

    Returns:
        A dict containing the prediction data for the player
    """
    name = await functions.to_jagex_name(name)
    sql: Select = select(dbPrediction)
    sql = sql.where(dbPrediction.name == name)

    async with PLAYERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            data = await session.execute(sql)

    data = sqlalchemy_result(data).rows2dict()
    keys = ["name", "Prediction", "id", "created"]
    data = [
        {k: float(v) / 100 if k not in keys else v for k, v in d.items()} for d in data
    ]
    if len(data) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Player not found"
        )

    data: dict = data[0]
    prediction = data.pop("Prediction")
    data = {
        "player_id": data.pop("id"),
        "player_name": data.pop("name"),
        "prediction_label": prediction,
        "prediction_confidence": data.pop("Predicted_confidence"),
        "created": data.pop("created"),
        "predictions_breakdown": data
        if breakdown or prediction != "Stats_Too_Low"
        else None,
    }

    prediction = data.get("prediction_label")

    if prediction == "Stats_Too_Low":
        # never show confidence if stats to low
        data["prediction_confidence"] = None
        if not breakdown:
            data["predictions_breakdown"] = None

    return data


@router.post("/prediction", tags=["Prediction"])
async def insert_prediction_into_plugin_database(
    token: str, prediction: List[Prediction], request: Request
):
    """
    Posts a new prediction into the plugin database.\n
    Use: Can be used to insert a new prediction into the plugin database.
    """
    await verify_token(
        token,
        verification="verify_ban",
        route=logging_helpers.build_route_log_string(request),
    )

    data = [d.dict() for d in prediction]

    columns = list_to_string([k for k in data[0].keys()])
    values = list_to_string([f":{k}" for k in data[0].keys()])

    sql = f"""replace into Predictions ({columns}) values ({values})"""
    sql = text(sql)

    async with PLAYERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            data = await session.execute(sql, data)

    return {"ok": "ok"}


@router.get("/prediction/data", tags=["Business"])
async def get_expired_predictions(token: str, limit: int = Query(50_000, ge=1)):
    """
    Select predictions where prediction data is not from today or null.
    Business service: ML
    """
    await verify_token(token, verification="request_highscores")

    # query
    columns_to_select = [PlayerHiscoreDataLatest, Player.name]
    sql: Select = select(*columns_to_select)
    sql = sql.where(
        or_(
            func.date(dbPrediction.created) != func.curdate(),
            dbPrediction.created == None,
        )
    )
    sql = sql.order_by(func.rand())
    sql = sql.limit(limit).offset(0)
    sql = sql.join(Player).join(dbPrediction, isouter=True)

    async with PLAYERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            data = await session.execute(sql)

    names, objs, output = [], [], []
    for d in data:
        objs.append((d[0],))
        names.append(d[1])

    data = sqlalchemy_result(objs).rows2dict()

    for d, n in zip(data, names):
        d["name"] = n
        output.append(d)

    return output


@router.get("/prediction/bulk", tags=["Prediction"])
async def gets_predictions_by_player_features(
    token: str,
    request: Request,
    row_count: int = Query(100_000, ge=1),
    page: int = Query(1, ge=1),
    possible_ban: Optional[int] = Query(None, ge=0, le=1),
    confirmed_ban: Optional[int] = Query(None, ge=0, le=1),
    confirmed_player: Optional[int] = Query(None, ge=0, le=1),
    label_id: Optional[int] = Query(None, ge=0),
    label_jagex: Optional[int] = Query(None, ge=0, le=5),
):
    """
    Get predictions by player features
    """
    await verify_token(
        token,
        verification="request_highscores",
        route=logging_helpers.build_route_log_string(request),
    )

    if (
        None
        == possible_ban
        == confirmed_ban
        == confirmed_player
        == label_id
        == label_jagex
    ):
        raise HTTPException(status_code=404, detail="No param given")
    # query
    sql: Select = select(dbPrediction)

    # filters
    if not possible_ban is None:
        sql = sql.where(Player.possible_ban == possible_ban)

    if not confirmed_ban is None:
        sql = sql.where(Player.confirmed_ban == confirmed_ban)

    if not confirmed_player is None:
        sql = sql.where(Player.confirmed_player == confirmed_player)

    if not label_id is None:
        sql = sql.where(Player.label_id == label_id)

    if not label_jagex is None:
        sql = sql.where(Player.label_jagex == label_jagex)

    # paging
    sql = sql.limit(row_count).offset(row_count * (page - 1))

    # join
    sql = sql.join(Player)

    # execute query
    async with PLAYERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            data = await session.execute(sql)

    data = sqlalchemy_result(data)
    return data.rows2dict()
