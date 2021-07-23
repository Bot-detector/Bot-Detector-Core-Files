from fastapi import APIRouter

router = APIRouter()

@router.get("/report", tags=["report"])
async def get():
    '''
    select data from database
    '''
    pass

@router.put("/report", tags=["report"])
async def put():
    '''
    update data into database
    '''
    # can be used for name change
    pass

@router.post("/report", tags=["report"])
async def post():
    '''
    insert data into database
    '''
    pass
