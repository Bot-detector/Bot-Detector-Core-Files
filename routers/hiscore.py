from fastapi import APIRouter

router = APIRouter()

@router.get("/hiscore", tags=["hiscore"])
async def get():
    '''
    select data from database
    '''
    pass

@router.get("/hiscoreLatest", tags=["hiscore"])
async def get():
    '''
    select data from database
    '''
    pass

@router.get("/hiscoreExpGain", tags=["hiscore"])
async def get():
    '''
    select data from database
    '''
    pass

@router.post("/hiscore", tags=["hiscore"])
async def post():
    '''
    insert data into database
    '''
    pass