from fastapi import APIRouter
from database.functions import execute_sql, verify_token
router = APIRouter()

@router.get("/v1/prediction", tags=["prediction"])
async def get(token: str):
    '''
    select data from database
    '''
    await verify_token(token, verifcation='hiscore')
    pass

@router.put("/v1/prediciton", tags=["prediction"])
async def put(token: str):
    '''
    update data into database
    '''
    await verify_token(token, verifcation='hiscore')
    pass

@router.post("/v1/prediction", tags=["prediction"])
async def post(token: str):
    '''
    insert data into database
    '''
    await verify_token(token, verifcation='hiscore')
    pass

@router.get("/v1/prediction/data", tags=["prediction", "business-logic"])
async def get(token: str):
    '''
        GET: the hiscore data where prediction is not from today
    '''
    await verify_token(token, verifcation='hiscore')
    sql = '''
        SELECT
            phd.*
        from Players pl 
        INNER JOIN playerHiscoreDataLatest phd on (pl.id = phd.Player_id)
        LEFT JOIN Predictions pr on (pl.id = pr.id)
        where 1=1
            and date(pr.created) != curdate()
        order by rand()
    '''
    data = await execute_sql(sql, row_count=5000)
    return data.rows2dict()
