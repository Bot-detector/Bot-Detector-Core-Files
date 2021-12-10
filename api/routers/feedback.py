from datetime import datetime
from typing import Optional

from api.database.database import Engine
from api.database.functions import execute_sql, list_to_string, verify_token, sqlalchemy_result
from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel
from api.database.models import PredictionsFeedback as dbFeedback
from sqlalchemy.sql.expression import insert, select


class Feedback(BaseModel):
    player_name: str
    vote: int
    prediction: str
    confidence: float
    subject_id: int
    feedback_text: Optional[str] = None
    proposed_label: Optional[str] = None


router = APIRouter()

@router.get("/v1/feedback/", tags=["feedback"])
async def get(
    token:str, 
    since_id:int=None, 
    since_date:datetime=None, 
    voter_id:int=None, 
    subject_id:int=None,
    has_text:bool=None, 
    row_count:int=100_000, 
    page:int=1
):
    '''
    select data from database
    '''
    await verify_token(token, verifcation='hiscore')

    # return exception if no param are given
    if None == since_id == since_date == voter_id == subject_id == has_text:
        raise HTTPException(
            status_code=400, detail="No valid parameters given")

    # create query
    sql = select(dbFeedback)

    # filters
    if not since_id == None:
        sql = sql.where(dbFeedback.id > since_id)

    if not since_date == None:
        sql = sql.where(dbFeedback.ts > since_date)

    if not voter_id == None:
        sql = sql.where(dbFeedback.voter_id == voter_id)

    if not subject_id == None:
        sql = sql.where(dbFeedback.subject_id == voter_id)

    if not has_text == None:
        sql = sql.where(dbFeedback.feedback_text != None)

    # query pagination
    sql = sql.limit(row_count).offset(row_count*(page-1))


    # transaction
    Session = Engine().session

    async with Session() as session:
        data = await session.execute(sql)

    data = sqlalchemy_result(data)

    return data.rows2dict()


@router.post("/v1/feedback/", status_code=status.HTTP_201_CREATED, tags=["feedback"])
async def post(feedback: Feedback, token:str):
    '''
    insert data into database
    '''
    await verify_token(token, verifcation='ban')
    feedback_params = feedback.dict()

    voter_data = await execute_sql(sql=f"select * from Players where name = :player_name", param={"player_name": feedback_params.pop("player_name")})
    voter_data = voter_data.rows2dict()[0]

    feedback_params["voter_id"] = voter_data.get("id")
    exclude = ["player_name"]

    columns = [k for k,v in feedback_params.items() if v is not None and k not in exclude]
    columns = list_to_string(columns)

    values = [f':{k}' for k,v in feedback_params.items() if v is not None and k not in exclude]
    values = list_to_string(values)

    sql = (f'''
        insert ignore into PredictionsFeedback ({columns})
        values ({values}) 
    ''')

    await execute_sql(sql, param=feedback_params)
    
    return {"OK": "OK"}