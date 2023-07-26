from pydantic import BaseModel
from typing import Optional


class Report(BaseModel):
    ID: int
    created_at: str
    reportedID: int
    reportingID: int
    region_id: int
    x_coord: int
    y_coord: int
    z_coord: int
    timestamp: str
    manual_detect: Optional[bool]  # TINYINT(1) can be converted to bool (True/False)
    on_members_world: Optional[int]
    on_pvp_world: Optional[bool]  # TINYINT can be converted to bool (True/False)
    world_number: Optional[int]
    equip_head_id: Optional[int]
    equip_amulet_id: Optional[int]
    equip_torso_id: Optional[int]
    equip_legs_id: Optional[int]
    equip_boots_id: Optional[int]
    equip_cape_id: Optional[int]
    equip_hands_id: Optional[int]
    equip_weapon_id: Optional[int]
    equip_shield_id: Optional[int]
    equip_ge_value: Optional[int]
