from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .db import SessionLocal, init_db
from . import models
from .schemas import PlayerOut, SuggestionOut, PickIn, PickOut
from .ingest import fantasypros, sleeper, news_free, injuries_free
from .services.ranking_blend import ensure_default_blend, blended_rank_for_player
from .services.suggestions import top_suggestions
from .services.exports import export_all_picks

import re
from rapidfuzz import process

app = FastAPI(title="Draft Assistant API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/api/status")
def status():
    return {"ok": True}

@app.post("/api/refresh")
def refresh_data(db: Session = Depends(get_db)):
    # Fetch Sleeper players for IDs (real dataset)
    s_data = sleeper.fetch_players()

    # Flatten to minimal rows
    def clean_nm(n): 
        return re.sub(r"[^A-Za-z\-\.' ]","", (n or "")).strip()
    # Build/Upsert players table
    for pid, pdata in s_data.items():
        full_name = pdata.get("full_name") or pdata.get("first_name","") + " " + pdata.get("last_name","" )
        pos = pdata.get("position") or pdata.get("fantasy_positions",[None])[0]
        team = (pdata.get("team") or "FA").upper()
        bye = pdata.get("bye_week") if isinstance(pdata.get("bye_week"), int) else None
        if not full_name or not pos:
            continue
        p = db.get(models.Player, pid)
        if not p:
            p = models.Player(player_id=pid)
        p.clean_name = clean_nm(full_name)
        p.position = pos
        p.team = team
        p.bye_week = bye
        db.merge(p)
    db.commit()

    # FantasyPros ECR + tiers (real page)
    ecr_df = fantasypros.fetch_ecr_and_tiers()

    # FantasyPros Half-PPR ADP (real page)
    adp_df = fantasypros.fetch_adp_half()

    # Optional Best Ball ADP (as Underdog proxy)
    try:
        bb_df = fantasypros.fetch_bestball_adp()
    except Exception:
        bb_df = None

    # Build a simple name -> player_id index via fuzzy match
    all_players = db.query(models.Player).all()
    name_to_pid = {p.clean_name: p.player_id for p in all_players}
    pnames = list(name_to_pid.keys())

    def match_pid(clean_name: str) -> str | None:
        if clean_name in name_to_pid:
            return name_to_pid[clean_name]
        # fuzzy
        if not pnames:
            return None
        res = process.extractOne(clean_name, pnames, score_cutoff=85)
        if res:
            return name_to_pid.get(res[0])
        return None

    # Upsert ECR
    for _, row in ecr_df.iterrows():
        pid = match_pid(str(row["clean_name"]).strip())
        if not pid:
            continue
        cr = db.query(models.ConsensusRank).filter_by(player_id=pid).first()
        if not cr:
            cr = models.ConsensusRank(player_id=pid)
        cr.ecr_rank = int(row.get("ecr_rank", None)) if str(row.get("ecr_rank","" )).isdigit() else None
        cr.tier = int(row.get("tier",  None)) if str(row.get("tier","" )).isdigit() else None
        cr.source = "fantasypros"
        db.merge(cr)
    db.commit()

    # Upsert ADP (half)
    for _, row in adp_df.iterrows():
        pid = match_pid(str(row["clean_name"]).strip())
        if not pid:
            continue
        adp = db.query(models.ADP).filter_by(player_id=pid, source="fantasypros_half").first()
        if not adp:
            adp = models.ADP(player_id=pid, source="fantasypros_half")
        try:
            adp_val = float(row.get("adp"))
        except Exception:
            continue
        adp.adp = adp_val
        db.merge(adp)
    db.commit()

    # Upsert ADP (bestball)
    if bb_df is not None:
        for _, row in bb_df.iterrows():
            pid = match_pid(str(row["clean_name"]).strip())
            if not pid:
                continue
            adp = db.query(models.ADP).filter_by(player_id=pid, source="fantasypros_bestball").first()
            if not adp:
                adp = models.ADP(player_id=pid, source="fantasypros_bestball")
            try:
                adp_val = float(row.get("adp"))
            except Exception:
                continue
            adp.adp = adp_val
            db.merge(adp)
        db.commit()

    # Very light news + injury proxy
    news_items = news_free.fetch_latest_news(limit=50)
    # Build a mapping clean_name -> pid for scoring
    player_name_index = {p.clean_name: p.player_id for p in all_players}
    risk_scores = {}
    try:
        risk_scores = injuries_free.fetch_injury_scores_for_players(player_name_index)
    except Exception:
        risk_scores = {}

    for cname, risk in risk_scores.items():
        pid = player_name_index.get(cname)
        if not pid:
            continue
        inj = db.query(models.Injury).filter_by(player_id=pid).first()
        if not inj:
            inj = models.Injury(player_id=pid)
        inj.risk_score = float(risk)
        inj.status = None
        db.merge(inj)
    db.commit()

    ensure_default_blend(db)

    return {"ok": True, "players": len(all_players)}

@app.get("/api/players", response_model=list[PlayerOut])
def list_players(position: str | None = None, db: Session = Depends(get_db)):
    q = db.query(models.Player)
    if position:
        q = q.filter(models.Player.position == position)
    res = []
    for p in q.all():
        cr = db.query(models.ConsensusRank).filter_by(player_id=p.player_id).first()
        # Choose best ADP available
        adp_half = db.query(models.ADP).filter_by(player_id=p.player_id, source="fantasypros_half").first()
        adp_val = adp_half.adp if adp_half else None
        res.append(PlayerOut(
            player_id=p.player_id,
            clean_name=p.clean_name,
            position=p.position,
            team=p.team,
            tier=cr.tier if cr else None,
            ecr_rank=cr.ecr_rank if cr else None,
            blended_rank=blended_rank_for_player(db, p.player_id),
            adp=adp_val
        ))
    # sort by blended then ecr
    res.sort(key=lambda r: (r.blended_rank if r.blended_rank is not None else 9999, r.ecr_rank if r.ecr_rank is not None else 9999))
    return res

@app.get("/api/suggestions", response_model=SuggestionOut)
def suggestions(db: Session = Depends(get_db)):
    top, nxt = top_suggestions(db, 3, 10)
    def to_out(p):
        cr = db.query(models.ConsensusRank).filter_by(player_id=p.player_id).first()
        adp_half = db.query(models.ADP).filter_by(player_id=p.player_id, source="fantasypros_half").first()
        return PlayerOut(
            player_id=p.player_id,
            clean_name=p.clean_name,
            position=p.position,
            team=p.team,
            tier=cr.tier if cr else None,
            ecr_rank=cr.ecr_rank if cr else None,
            blended_rank=blended_rank_for_player(db, p.player_id),
            adp=adp_half.adp if adp_half else None
        )
    return SuggestionOut(top=[to_out(p) for p in top], next=[to_out(p) for p in nxt])

@app.post("/api/picks", response_model=PickOut)
def add_pick(payload: PickIn, db: Session = Depends(get_db)):
    # Validate player exists
    p = db.get(models.Player, payload.player_id)
    if not p:
        raise HTTPException(status_code=404, detail="Player not found")
    pk = models.Pick(round_no=payload.round_no, overall_no=payload.overall_no, team_slot_id=payload.team_slot_id, player_id=payload.player_id)
    db.add(pk); db.commit(); db.refresh(pk)
    return PickOut(pick_id=pk.pick_id, round_no=pk.round_no, overall_no=pk.overall_no, team_slot_id=pk.team_slot_id, player_id=pk.player_id)

@app.get("/api/picks", response_model=list[PickOut])
def get_picks(db: Session = Depends(get_db)):
    out = []
    for pk in db.query(models.Pick).order_by(models.Pick.overall_no.asc()).all():
        out.append(PickOut(
            pick_id=pk.pick_id,
            round_no=pk.round_no,
            overall_no=pk.overall_no,
            team_slot_id=pk.team_slot_id,
            player_id=pk.player_id
        ))
    return out

@app.delete("/api/picks/{pick_id}")
def delete_pick(pick_id: int, db: Session = Depends(get_db)):
    pk = db.get(models.Pick, pick_id)
    if not pk:
        raise HTTPException(status_code=404, detail="Pick not found")
    db.delete(pk); db.commit()
    return {"ok": True}

@app.post("/api/export/picks")
def export_picks(db: Session = Depends(get_db)):
    path = export_all_picks(db)
    return {"ok": True, "path": path}
