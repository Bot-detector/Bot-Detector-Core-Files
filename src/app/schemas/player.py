from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class Player(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    created_at: datetime
    updated_at: Optional[datetime]
    possible_ban: bool
    confirmed_ban: bool
    confirmed_player: bool
    label_id: int
    label_jagex: int
