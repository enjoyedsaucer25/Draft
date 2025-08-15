from pydantic import BaseModel
from typing import Optional, List

class PlayerOut(BaseModel):
    player_id: str
    clean_name: str
    position: str
    team: str
    tier: Optional[int] = None
    ecr_rank: Optional[int] = None
    blended_rank: Optional[float] = None
    adp: Optional[float] = None

class SuggestionOut(BaseModel):
    top: List[PlayerOut]
    next: List[PlayerOut]

class PickIn(BaseModel):
    round_no: int
    overall_no: int
    team_slot_id: int
    player_id: str

class PickOut(BaseModel):
    pick_id: int
    round_no: int
    overall_no: int
    team_slot_id: int
    player_id: str
