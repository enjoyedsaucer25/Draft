from .news_free import fetch_latest_news

INJURY_KEYWORDS = [
    "hamstring","knee","ankle","concussion","groin","back","shoulder","wrist",
    "questionable","doubtful","limited","did not practice","DNP","MRI","out for",
]

def score_injury_risk(news_items: list[str]) -> float:
    """Simple keyword-based injury risk proxy: 0 (low) to 1 (high)."""
    if not news_items:
        return 0.2
    text = " ".join([n.get("headline","") for n in news_items]).lower()
    hits = sum(1 for k in INJURY_KEYWORDS if k in text)
    return min(1.0, 0.2 + 0.1*hits)

def fetch_injury_scores_for_players(player_name_index: dict[str, str]) -> dict[str, float]:
    """Map clean_name -> risk score. This is a coarse public-source approximation."""
    items = fetch_latest_news(limit=100)
    risk = {}
    for clean_name in player_name_index.keys():
        # naive match
        matches = [it for it in items if clean_name.lower().split(" ")[0] in it.get("headline"," ").lower()]
        risk[clean_name] = score_injury_risk(matches)
    return risk
