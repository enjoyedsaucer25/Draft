from sqlalchemy.orm import Session
from ..models import TeamLeague, Pick, Player
from collections import Counter

def team_needs(db: Session, team_slot_id: int):
    # Simplified: counts positions drafted vs required
    req = {"QB":1,"RB":2,"WR":3,"TE":0,"FLEX":1,"K":1,"DEF":1}
    picks = db.query(Pick).filter_by(team_slot_id=team_slot_id).all()
    pos_counts = Counter()
    for pk in picks:
        p = db.query(Player).filter_by(player_id=pk.player_id).first()
        if p:
            pos_counts[p.position] += 1
    needs = {k: max(0, v - pos_counts.get(k,0)) for k,v in req.items()}
    return needs

def run_prediction(db: Session, upcoming_team_ids: list[int]) -> dict:
    # Count how many of next teams need each position
    pos_need = Counter()
    for tid in upcoming_team_ids:
        n = team_needs(db, tid)
        for k,v in n.items():
            if v > 0:
                pos_need[k] += 1
    return dict(pos_need)
