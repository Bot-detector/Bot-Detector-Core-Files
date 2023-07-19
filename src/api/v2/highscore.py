from fastapi import APIRouter, Query, status
from src.app.repositories.highscore import (
    PlayerHiscoreData as RepositoryPlayerHiscoreData,
)
from src.app.schemas.highscore import PlayerHiscoreData as SchemaPlayerHiscoreData
from pydantic import BaseModel

router = APIRouter(tags=["Hiscore"])


@router.get("/hiscore", response_model=list[SchemaPlayerHiscoreData])
async def get_highscore_data(
    player_name: str = Query(..., max_length=13),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=1000),
):
    repo = RepositoryPlayerHiscoreData()
    data = await repo.read(player_name=player_name, page=page, page_size=page_size)
    return data


@router.post("/hiscore", status_code=status.HTTP_201_CREATED)
async def post_highscore_data(data: list[SchemaPlayerHiscoreData]):
    repo = RepositoryPlayerHiscoreData()
    await repo.create(data=data)
    return
