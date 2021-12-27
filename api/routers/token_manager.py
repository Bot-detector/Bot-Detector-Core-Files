from datetime import datetime
import time
from typing import List, Optional

from sqlalchemy.sql.sqltypes import BIGINT, TIMESTAMP

from api.database.database import Engine, EngineType, get_session
from api.database.functions import sqlalchemy_result, verify_token
from api.database.models import ApiPermission as dbApiPermission,\
                                ApiUsage as dbApiUsage,\
                                ApiUser as dbApiUser,\
                                ApiUserPerm as dbApiUserPerm 
                                
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.sql.expression import insert, select, update

router = APIRouter()

class ApiPermission(BaseModel):
    permission : str

class ApiUser(BaseModel):
    username : str
    token : str
    ratelimit : Optional[int] = 100
    is_active : Optional[int] = 0
    
class ApiUsage(BaseModel):
    user_id : int
    timestamp : Optional[datetime]
    route : Optional[str]

class ApiUserPerm(BaseModel):
    user_id : int
    permission_id : int

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
    await verify_token(auth_token, verification='admin', route=f'[GET]/v1/token-management/get-token-data')

    # create query
    sql = select(dbApiUser)
    
    # Filters
    if target_token is not None:
        sql = sql.where(dbApiUser.token == target_token)
    if examine_username is not None:
        sql = sql.where(dbApiUser.username == examine_username)
    if examine_userID is not None:
        sql = sql.where(dbApiUser.ID== examine_userID)

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
    await verify_token(auth_token, verification='admin', route=f'[GET]/v1/token-management/get-token-usage')

    # create query
    sql = select(dbApiUsage)
    
    # Filters
    if user_id is not None:
        sql = sql.where(dbApiUsage.user_id == user_id)
    if route is not None:
        sql = sql.where(dbApiUsage.route == route)
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
    await verify_token(auth_token, verification='admin', route=f'[GET]/v1/token-management/get-permissions')

    # create query
    sql = select(dbApiPermission)

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
    await verify_token(auth_token, verification='admin', route=f'[GET]/v1/token-management/get-token-permissions')

    # create query
    sql = select(dbApiUserPerm)
    
    if user_id is not None:
        sql = sql.where(dbApiUserPerm.user_id == user_id)
    if permission_id is not None:
        sql = sql.where(dbApiUserPerm.permission_id == permission_id)

    # transaction
    async with get_session(EngineType.PLAYERDATA) as session:
        data = await session.execute(sql)

    data = sqlalchemy_result(data)
    return data.rows2dict()

"""
    Token post routes
"""

@router.post("/v1/token-management/create-token", tags=["Token Management"])
async def create_token(auth_token:str, create_token: ApiUser):
    '''
        Create a new token
    '''
    await verify_token(auth_token, verification='admin', route='[POST]/v1/token-management/create-token')
    
    create_token = create_token.dict()
    sql_insert = insert(dbApiUser)
    sql_insert = sql_insert.values(create_token)

    async with get_session(EngineType.PLAYERDATA) as session:
        await session.execute(sql_insert)
        await session.commit()

    return {"OK": "OK"}

@router.post("/v1/token-management/create-permission", tags=["Token Management"])
async def create_permission(auth_token:str, create_permission: ApiPermission):
    '''
        Create a new permission
    '''
    await verify_token(auth_token, verification='admin', route='[POST]/v1/token-management/create-permission')
    
    create_permission = create_permission.dict()
    sql_insert = insert(dbApiPermission)
    sql_insert = sql_insert.values(create_permission)

    async with get_session(EngineType.PLAYERDATA) as session:
        await session.execute(sql_insert)
        await session.commit()

    return {"OK": "OK"}

@router.post("/v1/token-management/create-user-permission", tags=["Token Management"])
async def create_user_permission(auth_token:str, create_user_permission: ApiUserPerm):
    '''
        Create a new user permission
    '''
    await verify_token(auth_token, verification='admin', route='[POST]/v1/token-management/create-user-permission')
    
    create_user_permission = create_user_permission.dict()
    sql_insert = insert(dbApiUserPerm)
    sql_insert = sql_insert.values(create_user_permission)

    async with get_session(EngineType.PLAYERDATA) as session:
        await session.execute(sql_insert)
        await session.commit()

    return {"OK": "OK"}

@router.post("/v1/token-management/create-user-usage", tags=["Token Management"])
async def create_user_usage(auth_token:str, create_user_usage: ApiUsage):
    '''
        Create a new user usage log
    '''
    await verify_token(auth_token, verification='admin', route='[POST]/v1/token-management/create-user-usage')
    
    create_user_usage = create_user_usage.dict()
    sql_insert = insert(dbApiUsage)
    sql_insert = sql_insert.values(create_user_usage)

    async with get_session(EngineType.PLAYERDATA) as session:
        await session.execute(sql_insert)
        await session.commit()

    return {"OK": "OK"}

"""
    Token put routes
"""

"""
    Token delete routes
"""