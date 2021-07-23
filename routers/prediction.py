from fastapi import APIRouter

router = APIRouter()

@router.get("/prediction", tags=["prediction"])
async def get():
    '''
    select data from database
    '''
    pass

@router.put("/prediciton", tags=["prediction"])
async def put():
    '''
    update data into database
    '''
    pass

@router.post("/prediction", tags=["prediction"])
async def post():
    '''
    insert data into database
    '''
    pass
