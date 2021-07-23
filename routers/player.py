from fastapi import APIRouter

router = APIRouter()

@router.get("/player", tags=["player"])
async def get():
    '''
    select data from database
    '''
    pass

@router.put("/player", tags=["player"])
async def put():
    '''
    update data into database
    '''
    pass

@router.post("/player", tags=["player"])
async def post():
    '''
    insert data into database
    '''
    pass
