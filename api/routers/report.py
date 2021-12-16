import logging
from typing import List

from api.database.functions import execute_sql, verify_token
from fastapi import APIRouter
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter()


class equipment(BaseModel):
    equip_head_id: int
    equip_amulet_id: int
    equip_torso_id: int
    equip_legs_id: int
    equip_boots_id: int
    equip_cape_id: int
    equip_hands_id: int
    equip_weapon_id: int
    equip_shield_id: int


class detection(BaseModel):
    reportedID: int
    reportingID: int
    region_id: int
    x_coord: int
    y_coord: int
    z_coord: int
    ts: int
    manual_detect: int
    on_members_world: int
    on_pvp_world: int
    world_number: int
    equipment: equipment
    equip_ge_value: int


@router.get("v1/report", tags=["report"])
async def get(token: str):
    '''
    select data from database
    '''
    await verify_token(token, verifcation='hiscore')
    pass


@router.put("v1/report", tags=["report"])
async def put(old_user_id: int, new_user_id: int, token: str):
    '''
    update data into database
    '''
    await verify_token(token, verifcation='ban')
    # can be used for name change
    sql = ('''
    UPDATE Reports
    SET
        reportingID = :NewUser
    where 
        reportingID = :OldUser

    ''')
    param = {}
    param['NewUser'] = new_user_id
    param['OldUser'] = old_user_id

    await execute_sql(sql, param)
    return {'OK':'OK'}


@router.post("v1/report", tags=["report"])
async def post(token:str,detections: List[detection]):
    '''
    insert data into database
    '''
    await verify_token(token, verifcation='ban')
    sql = ('''
        insert ignore into Reports
    ''')

    if len(detections) > 5000:
        return {'OK':'OK'}
        
    pass
