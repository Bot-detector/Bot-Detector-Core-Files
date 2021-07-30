from fastapi import APIRouter

router = APIRouter()

@router.get("v1/player", tags=["player"])
async def get():
    '''
    select data from database
    '''
    pass

@router.put("v1/player", tags=["player"])
async def put():
    '''
    update data into database
    '''
    pass

@router.post("v1/player", tags=["player"])
async def post():
    '''
    insert data into database
    '''
    pass
