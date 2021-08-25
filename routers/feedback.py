from typing import Optional

from database.functions import execute_sql, list_to_string
from fastapi import APIRouter, status
from pydantic import BaseModel


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
async def get():
    '''
    select data from database
    '''
    pass


@router.post("/v1/feedback/", status_code=status.HTTP_201_CREATED, tags=["feedback"])
async def post(feedback: Feedback):
    '''
    insert data into database
    '''
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

    print(sql)
    print(feedback_params)

    await execute_sql(sql, param=feedback_params, debug=True)
    
    return {"OK": "OK"}