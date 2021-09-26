from fastapi import APIRouter
from database.functions import verify_token
router = APIRouter()

@router.get("v1/prediction", tags=["prediction"])
async def get(token: str):
    '''
    select data from database
    '''
    await verify_token(token, verifcation='hiscore')
    pass

@router.put("v1/prediciton", tags=["prediction"])
async def put(token: str):
    '''
    update data into database
    '''
    await verify_token(token, verifcation='hiscore')
    pass

@router.post("v1/prediction", tags=["prediction"])
async def post(token: str):
    '''
    insert data into database
    '''
    await verify_token(token, verifcation='hiscore')
    pass
