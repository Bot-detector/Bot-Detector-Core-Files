from fastapi import APIRouter

router = APIRouter()

@router.get("v1/feedback", tags=["feedback"])
async def get():
    '''
    select data from database
    '''
    pass

@router.post("v1/feedback", tags=["feedback"])
async def post():
    '''
    insert data into database
    '''
    pass
