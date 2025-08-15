from sqlalchemy.orm import Session
from ..models import Player, ConsensusRank, ADP, BlendSettings
from typing import Dict

def ensure_default_blend(db: Session):
    if not db.query(BlendSettings).first():
        bs = BlendSettings(sleeper_wt=0.0, fpros_wt=0.8, udog_wt=0.2, enabled=True, smoothing_days=7)
        db.add(bs); db.commit()

def blended_rank_for_player(db: Session, player_id: str) -> float | None:
    # Blend: ecr rank (fantasypros) and adp sources (half + bestball)
    ecr = db.query(ConsensusRank).filter_by(player_id=player_id).first()
    adp_half = db.query(ADP).filter_by(player_id=player_id, source="fantasypros_half").first()
    adp_bb = db.query(ADP).filter_by(player_id=player_id, source="fantasypros_bestball").first()
    bs = db.query(BlendSettings).first()
    if not bs:
        return ecr.ecr_rank if ecr else None
    # Normalize to ranks (lower is better); ADP is already positional value (lower=earlier).
    vals = []
    wts = []
    if ecr and bs.fpros_wt > 0:
        vals.append(float(ecr.ecr_rank))
        wts.append(bs.fpros_wt * 0.5)  # split fpros weight across ecr/adp
    if adp_half and bs.fpros_wt > 0:
        vals.append(float(adp_half.adp))
        wts.append(bs.fpros_wt * 0.5)
    if adp_bb and bs.udog_wt > 0:
        vals.append(float(adp_bb.adp))
        wts.append(bs.udog_wt)
    if not vals:
        return ecr.ecr_rank if ecr else None
    # Weighted average
    num = sum(v*w for v,w in zip(vals,wts))
    den = sum(wts)
    return num/den if den else None
