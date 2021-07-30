from fastapi import APIRouter

router = APIRouter()

@router.get("v1/prediction", tags=["prediction"])
async def get():
    '''
    select data from database
    '''
    pass

@router.put("v1/prediciton", tags=["prediction"])
async def put():
    '''
    update data into database
    '''
    pass

@router.post("v1/prediction", tags=["prediction"])
async def post():
    '''
    insert data into database
    '''
    pass
