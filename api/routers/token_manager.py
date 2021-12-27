import time
from typing import List, Optional

from sqlalchemy.sql.sqltypes import TIMESTAMP

from api.database.database import Engine, EngineType, get_session
from api.database.functions import sqlalchemy_result, verify_token
from api.database.models import ApiPermission, ApiUsage, ApiUser, ApiUserPerm
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.sql.expression import insert, select, update

router = APIRouter()

"""
    Token get routes for management
"""

@router.get("/v1/token-management/get-token-data", tags=["Token Management"])
async def get_tokens(
    auth_token: str,
    target_token: Optional[str] = None,
    examine_username: Optional[str] = None,
    examine_userID: Optional[int] = Query(None, ge=0),
    ):
    '''
        Select tokens and display data for panel
    '''
    await verify_token(auth_token, verification='admin', route=f'[GET]/v1/token-management/get-token-data/')

    # create query
    sql = select(ApiUser)
    
    # Filters
    if target_token is not None:
        sql = sql.where(ApiUser.token == target_token)
    if examine_username is not None:
        sql = sql.where(ApiUser.username == examine_username)
    if examine_userID is not None:
        sql = sql.where(ApiUser.ID== examine_userID)

    # transaction
    async with get_session(EngineType.PLAYERDATA) as session:
        data = await session.execute(sql)

    data = sqlalchemy_result(data)
    return data.rows2dict()

@router.get("/v1/token-management/get-token-usage", tags=["Token Management"])
async def get_api_usage(
    auth_token: str,
    user_id: Optional[int] = None,
    route: Optional[str] = None,
    limit: Optional[int] = 10_000,
    ):
    '''
        Select token usage and display data for panel
    '''
    await verify_token(auth_token, verification='admin', route=f'[GET]/v1/token-management/get-token-data/')

    # create query
    sql = select(ApiUsage)
    
    # Filters
    if user_id is not None:
        sql = sql.where(ApiUsage.user_id == user_id)
    if route is not None:
        sql = sql.where(ApiUsage.route == route)
    if limit is not None:
        sql = sql.limit(limit)

    # transaction
    async with get_session(EngineType.PLAYERDATA) as session:
        data = await session.execute(sql)

    data = sqlalchemy_result(data)
    return data.rows2dict()

@router.get("/v1/token-management/get-permissions", tags=["Token Management"])
async def get_permissions(
    auth_token: str
    ):
    '''
        Select permissions list
    '''
    await verify_token(auth_token, verification='admin', route=f'[GET]/v1/token-management/get-token-data/')

    # create query
    sql = select(ApiPermission)

    # transaction
    async with get_session(EngineType.PLAYERDATA) as session:
        data = await session.execute(sql)

    data = sqlalchemy_result(data)
    return data.rows2dict()

@router.get("/v1/token-management/get-token-permissions", tags=["Token Management"])
async def get_token_permissions(
    auth_token: str,
    user_id: Optional[int] = None,
    permission_id: Optional[int] = None
    ):
    '''
        Select token-permission pairs
    '''
    await verify_token(auth_token, verification='admin', route=f'[GET]/v1/token-management/get-token-data/')

    # create query
    sql = select(ApiUserPerm)
    
    if user_id is not None:
        sql = sql.where(ApiUserPerm.user_id == user_id)
    if permission_id is not None:
        sql = sql.where(ApiUserPerm.permission_id == permission_id)

    # transaction
    async with get_session(EngineType.PLAYERDATA) as session:
        data = await session.execute(sql)

    data = sqlalchemy_result(data)
    return data.rows2dict()