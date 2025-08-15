from sqlalchemy.orm import Session
from ..models import Player, ConsensusRank, ADP, UserBoardOverride
from .ranking_blend import blended_rank_for_player
from typing import List, Tuple

# Roster config (snake draft): 1QB, 2RB, 3WR, 1FLEX, 1K, 1DEF
ROSTER_REQ = {"QB":1,"RB":2,"WR":3,"TE":0,"FLEX":1,"K":1,"DEF":1}

def priority_score(db: Session, p: Player) -> float:
    br = blended_rank_for_player(db, p.player_id)
    if br is None:
        br = 999.0
    # Lower is better; include small positional scarcity heuristic
    scarcity = {"QB":0.0,"RB":-2.0,"WR":-1.0,"TE":-0.5,"K":0.5,"DEF":0.5}.get(p.position,0.0)
    return br + scarcity

def top_suggestions(db: Session, limit_top=3, limit_next=10) -> Tuple[List[Player], List[Player]]:
    players = db.query(Player).all()
    ranked = sorted(players, key=lambda p: priority_score(db, p))
    return ranked[:limit_top], ranked[limit_top:limit_top+limit_next]
