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
from sqlalchemy.sql.expression import delete, insert, select, update

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
    route : Optional[str]

class ApiUserPerm(BaseModel):
    user_id : int
    permission_id : int

"""
    Token get routes for management
"""

@router.get("/security/token-management/get-token-data", tags=["Token Management"])
async def get_tokens(
    auth_token: str,
    target_token: Optional[str] = None,
    examine_username: Optional[str] = None,
    examine_userID: Optional[int] = Query(None, ge=0),
    ):
    '''
        Select token data
    '''
    await verify_token(auth_token, verification='admin', route=f'[GET]/security/token-management/get-token-data')

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

@router.get("/security/token-management/get-token-usage", tags=["Token Management"])
async def get_api_usage(
    auth_token: str,
    user_id: Optional[int] = None,
    route: Optional[str] = None,
    limit: Optional[int] = 10_000,
    ):
    '''
        Select token usage and display data for panel
    '''
    await verify_token(auth_token, verification='admin', route=f'[GET]/security/token-management/get-token-usage')

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

@router.get("/security/token-management/get-permissions", tags=["Token Management"])
async def get_permissions(
    auth_token: str
    ):
    '''
        Select permissions list
    '''
    await verify_token(auth_token, verification='admin', route=f'[GET]/security/token-management/get-permissions')

    # create query
    sql = select(dbApiPermission)

    # transaction
    async with get_session(EngineType.PLAYERDATA) as session:
        data = await session.execute(sql)

    data = sqlalchemy_result(data)
    return data.rows2dict()

@router.get("/security/token-management/get-token-permissions", tags=["Token Management"])
async def get_token_permissions(
    auth_token: str,
    user_id: Optional[int] = None,
    permission_id: Optional[int] = None
    ):
    '''
        Select token-permission pairs
    '''
    await verify_token(auth_token, verification='admin', route=f'[GET]/security/token-management/get-token-permissions')

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

@router.post("/security/token-management/create-token", tags=["Token Management"])
async def create_token(auth_token:str, create_token: ApiUser):
    '''
        Create a new token
    '''
    await verify_token(auth_token, verification='admin', route='[POST]/security/token-management/create-token')
    
    create_token = create_token.dict()
    sql_insert = insert(dbApiUser)
    sql_insert = sql_insert.values(create_token)

    async with get_session(EngineType.PLAYERDATA) as session:
        await session.execute(sql_insert)
        await session.commit()

    return {"OK": "OK"}

@router.post("/security/token-management/create-permission", tags=["Token Management"])
async def create_permission(auth_token:str, create_permission: ApiPermission):
    '''
        Create a new permission
    '''
    await verify_token(auth_token, verification='admin', route='[POST]/security/token-management/create-permission')
    
    create_permission = create_permission.dict()
    sql_insert = insert(dbApiPermission)
    sql_insert = sql_insert.values(create_permission)

    async with get_session(EngineType.PLAYERDATA) as session:
        await session.execute(sql_insert)
        await session.commit()

    return {"OK": "OK"}

@router.post("/security/token-management/create-user-permission", tags=["Token Management"])
async def create_user_permission(auth_token:str, create_user_permission: ApiUserPerm):
    '''
        Create a new user permission
    '''
    await verify_token(auth_token, verification='admin', route='[POST]/security/token-management/create-user-permission')
    
    create_user_permission = create_user_permission.dict()
    sql_insert = insert(dbApiUserPerm)
    sql_insert = sql_insert.values(create_user_permission)

    async with get_session(EngineType.PLAYERDATA) as session:
        await session.execute(sql_insert)
        await session.commit()

    return {"OK": "OK"}

@router.post("/security/token-management/create-user-usage", tags=["Token Management"])
async def create_user_usage(auth_token:str, create_user_usage: ApiUsage):
    '''
        Create a new user usage log
    '''
    await verify_token(auth_token, verification='admin', route='[POST]/security/token-management/create-user-usage')
    
    create_user_usage = create_user_usage.dict()
    sql_insert = insert(dbApiUsage)
    sql_insert = sql_insert.values(create_user_usage)

    async with get_session(EngineType.PLAYERDATA) as session:
        await session.execute(sql_insert)
        await session.commit()

    return {"OK": "OK"}

"""
    Token put routes
    Note: Only the update-token put route is required. The put route for logging should not be accessed as logs should not be modified.
    In addition, permissions can be added or deleted in order to be modified. Finally Permission names should be deleted, not modified,
    in order to prevent errors from occuring with child-parent relationships in the dbApiUserPerm table. 
"""

@router.put("/security/token-management/update-token", tags=["Token Management"])
async def update_token(
                        auth_token:str,
                        update_token: ApiUser
                       ):
    '''
        Update a token
    '''
    await verify_token(auth_token, verification='admin', route='[PUT]/security/token-management/update-token')
    
    update_token = update_token.dict()
    sql_update = update(dbApiUser)
    sql_update = sql_update.values(update_token)
    sql_update = sql_update.where(dbApiUser.username == update_token['username'])

    async with get_session(EngineType.PLAYERDATA) as session:
        await session.execute(sql_update)
        await session.commit()
        
    return {"OK": "OK"}

"""
    Token delete routes
"""

@router.delete("/security/token-management/delete-token", tags=["Token Management"])
async def delete_token(
                       auth_token:str,
                       id : int = Query(None, ge=0)
                       ):
    '''
        Delete a token\n
        NOTE: MUST DELETE ALL LINKED USER-PERMISSIONS PRIOR TO DELETING TOKEN.\n
        WARNING: IT IS RECOMMENDED TO INSTEAD SET THE USER TOKEN TO 'INACTIVE'.
    '''
    await verify_token(auth_token, verification='admin', route='[DELETE]/security/token-management/delete-token')
    
    if id is None:
        raise HTTPException(status_code=422, detail="Missing ID.")
    else:
        sql_delete = delete(dbApiUser).where(dbApiUser.id == id)
        async with get_session(EngineType.PLAYERDATA) as session:
            await session.execute(sql_delete)
            await session.commit()
        return {"OK": "OK"}

@router.delete("/security/token-management/delete-permission", tags=["Token Management"])
async def delete_permission(
                            auth_token:str,
                            id : int = Query(None, ge=0)
                            ):
    '''
        Delete a permission\n
        NOTE: MUST DELETE ALL LINKED USER-PERMISSIONS PRIOR TO DELETING PERMISSIONS.
    '''
    await verify_token(auth_token, verification='admin', route='[DELETE]/security/token-management/delete-permission')
    
    if id is None:
        raise HTTPException(status_code=422, detail="Missing ID.")
    else:
        sql_delete = delete(dbApiPermission).where(dbApiPermission.id == id)
        async with get_session(EngineType.PLAYERDATA) as session:
            await session.execute(sql_delete)
            await session.commit()
        return {"OK": "OK"}

@router.delete("/security/token-management/delete-user-permission", tags=["Token Management"])
async def delete_user_permission(
                                auth_token:str,
                                id : int = Query(None, ge=0)
                                ):
    '''
        Delete a user permission\n
        NOTE: USUALLY THE FIRST STEP IN REMOVING TOKEN PERMISSIONS FROM A USER.
    '''
    await verify_token(auth_token, verification='admin', route='[DELETE]/security/token-management/delete-user-permission')
    
    if id is None:
        raise HTTPException(status_code=422, detail="Missing ID.")
    else:
        sql_delete = delete(dbApiUserPerm).where(dbApiUserPerm.id == id)
        async with get_session(EngineType.PLAYERDATA) as session:
            await session.execute(sql_delete)
            await session.commit()
        return {"OK": "OK"}