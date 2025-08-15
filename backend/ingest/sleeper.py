import requests, json

URL_PLAYERS = "https://api.sleeper.app/v1/players/nfl"

def fetch_players() -> dict:
    """Return the Sleeper players dataset (dict keyed by player_id)."""
    r = requests.get(URL_PLAYERS, timeout=30)
    r.raise_for_status()
    data = r.json()
    # Sleeper returns a dict keyed by player_id (string)
    return data
