from fastapi import APIRouter

router = APIRouter()

@router.get("v1/hiscore", tags=["hiscore"])
async def get():
    '''
    select data from database
    '''
    pass

@router.get("v1/hiscoreLatest", tags=["hiscore"])
async def get():
    '''
    select data from database
    '''
    pass

@router.get("v1/hiscoreExpGain", tags=["hiscore"])
async def get():
    '''
    select data from database
    '''
    pass

@router.post("v1/hiscore", tags=["hiscore"])
async def post():
    '''
    insert data into database
    '''
    pass