from fastapi import APIRouter, Header, Query, Request, status
from fastapi.exceptions import HTTPException

from src.app.repositories.player import Player as RepositoryPlayer
from src.app.schemas.player import Player as SchemaPlayer
from src.database.functions import verify_token
from src.utils import logging_helpers

router = APIRouter(tags=["Player"])


@router.get("/player", response_model=list[SchemaPlayer])
async def get_player_data(
    request: Request,
    player_name: str = Query(..., max_length=13),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=1000),
    token: str = Header(...),
):
    await verify_token(
        token,
        verification="verify_ban",
        route=logging_helpers.build_route_log_string(request),
    )

    repo = RepositoryPlayer()
    data = await repo.read(player_name=player_name, page=page, page_size=page_size)
    return data


@router.get("/players", response_model=list[SchemaPlayer])
async def get_many_players_data(
    request: Request,
    page: int = Query(default=None),
    page_size: int = Query(default=10, ge=1, le=10_000),
    greater_than: int = Query(default=None),
    token: str = Header(...),
):
    await verify_token(
        token,
        verification="verify_ban",
        route=logging_helpers.build_route_log_string(request),
    )

    if greater_than is None and page is None:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=f"page or greater than required, received: {page=}, {greater_than=}",
        )

    if all([page, greater_than]):
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=f"either page or greater than not both can be set, received: {page=}, {greater_than=}",
        )

    repo = RepositoryPlayer()
    data = await repo.read_many(
        page=page, page_size=page_size, greater_than=greater_than
    )
    return data


@router.post("/player", status_code=status.HTTP_201_CREATED)
async def post_highscore_data(
    request: Request, data: list[SchemaPlayer], token: str = Header(...)
):
    await verify_token(
        token,
        verification="verify_ban",
        route=logging_helpers.build_route_log_string(request),
    )
    repo = RepositoryPlayer()
    await repo.create(data=data)
    return
