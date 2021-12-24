from typing import Optional

from api.database.functions import execute_sql, list_to_string, verify_token
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

@router.get("/v1/feedback/", tags=["Feedback Routes","Discord Routes"])
async def gets_feedback_from_plugin_database(token:str):
    '''
    Placeholder: Will get player feedback from the database.\n
    Use: This can be used to obtain prediction feedback for routes accessible to the plugin database, this can be used as a method of displaying predictions in the plugin discord, or on the plugin website.
    '''
    await verify_token(token, verification='verify_ban', route='[GET]/v1/feedback')
    pass


@router.post("/v1/feedback/", status_code=status.HTTP_201_CREATED, tags=["Feedback Routes","Plugin Routes"])
async def posts_new_feedback_to_plugin_database(feedback: Feedback, token:str):
    '''
    Inserts player's plugin prediction feedback into the database.\n
    Use: This route is usually accessed from the plugin which a user clicks on a player's text box and submits the correction or confirmation. The primary use of this route is through the Bot Detector Plugin itself.
    '''
    await verify_token(token, verification='verify_ban', route='[POST]/v1/feedback')
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
