import requests
import pandas as pd
from bs4 import BeautifulSoup
from rapidfuzz import fuzz
import re
from typing import Tuple, Dict, List

# Real pages (as of Aug 2025):
URL_ECR_HALF_OVERALL = "https://www.fantasypros.com/nfl/cheatsheets/top-half-ppr-players.php"
URL_ADP_HALF_OVERALL = "https://www.fantasypros.com/nfl/adp/half-point-ppr-overall.php"
URL_BESTBALL_ADP = "https://www.fantasypros.com/nfl/adp/best-ball-overall.php"

def _clean_name(txt: str) -> str:
    t = re.sub(r"\s+\(.*?\)", "", txt)  # remove '(team/bye)'
    t = re.sub(r"[^A-Za-z\-\.' ]", "", t)
    return t.strip()

def fetch_ecr_and_tiers() -> pd.DataFrame:
    """Fetch ECR + tiers from FantasyPros Half-PPR overall cheat sheet (real page)."""
    r = requests.get(URL_ECR_HALF_OVERALL, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")
    # The page has a list with overall rankings; fall back to tables if present
    # Attempt to parse ordered list first
    items = []
    for li in soup.select("ol li"):
        txt = li.get_text(" ", strip=True)
        # Expect format "1. Player Team-POS"
        m = re.match(r"^(\d+)\.?\s+(.*)$", txt)
        if not m:
            continue
        rank = int(m.group(1))
        name_part = m.group(2)
        name = _clean_name(name_part.split(" ")[0] if " " not in name_part else " ".join(name_part.split(" ")[:-1]))
        items.append({"ecr_rank": rank, "clean_name": name})
    if not items:
        # Fallback: try read_html on any table that looks like rankings
        dfs = pd.read_html(r.text)
        df = dfs[0]
    else:
        df = pd.DataFrame(items)
    # Tier inference: breakpoints every time rank jumps > 8 by default (simple elbow)
    df = df.sort_values("ecr_rank").reset_index(drop=True)
    tier = 1
    tiers = []
    prev = None
    for _, row in df.iterrows():
        rk = int(row["ecr_rank"])
        if prev and rk - prev > 8:
            tier += 1
        tiers.append(tier)
        prev = rk
    df["tier"] = tiers
    return df

def fetch_adp_half() -> pd.DataFrame:
    """Fetch Half-PPR ADP consensus table (real page)."""
    r = requests.get(URL_ADP_HALF_OVERALL, timeout=20)
    r.raise_for_status()
    # Prefer pandas html parsing for consistency
    dfs = pd.read_html(r.text)
    # Expect columns: Rank, Player Team (Bye), POS, Yahoo, Sleeper, RTSports, AVG
    df = dfs[0]
    # Normalize
    if "Player Team (Bye)" in df.columns:
        df["clean_name"] = df["Player Team (Bye)"].apply(lambda x: _clean_name(str(x).split("  ")[0]))
    elif "Player" in df.columns:
        df["clean_name"] = df["Player"].apply(lambda x: _clean_name(str(x)))
    else:
        # fallback: best-effort first column
        df["clean_name"] = df.iloc[:,1].astype(str).apply(_clean_name)
    # Standardize cols
    rename = {"AVG": "adp", "Avg": "adp", "Average": "adp", "Rank": "adp_rank"}
    for a,b in rename.items():
        if a in df.columns:
            df = df.rename(columns={a:b})
    if "adp" not in df.columns:
        # If no average col, compute from available sources
        srcs = [c for c in df.columns if c.lower() in {"yahoo","sleeper","rtsports","espn","fdp","bbm","underdog"}]
        if srcs:
            df["adp"] = df[srcs].apply(pd.to_numeric, errors="coerce").mean(axis=1)
    return df

def fetch_bestball_adp() -> pd.DataFrame:
    r = requests.get(URL_BESTBALL_ADP, timeout=20)
    r.raise_for_status()
    dfs = pd.read_html(r.text)
    df = dfs[0]
    # Standardize
    if "Player Team (Bye)" in df.columns:
        df["clean_name"] = df["Player Team (Bye)"].apply(lambda x: _clean_name(str(x).split("  ")[0]))
    if "Avg" in df.columns and "adp" not in df.columns:
        df = df.rename(columns={"Avg": "adp"})
    return df
