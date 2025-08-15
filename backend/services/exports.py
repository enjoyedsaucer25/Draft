from ..utils.excel_io import export_picks_csv
from sqlalchemy.orm import Session
from ..models import Pick

def export_all_picks(db: Session, path: str = "data/picks_export.csv"):
    rows = []
    for pk in db.query(Pick).order_by(Pick.overall_no.asc()).all():
        rows.append({
            "pick_id": pk.pick_id,
            "round_no": pk.round_no,
            "overall_no": pk.overall_no,
            "team_slot_id": pk.team_slot_id,
            "player_id": pk.player_id,
            "ts": pk.ts.isoformat(),
        })
    return export_picks_csv(rows, path)
