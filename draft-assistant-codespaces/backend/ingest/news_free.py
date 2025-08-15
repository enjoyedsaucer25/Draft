import requests
from bs4 import BeautifulSoup

NBC_PLAYER_NEWS = "https://www.nbcsports.com/fantasy/football/player-news"

def fetch_latest_news(limit: int = 25):
    """Lightweight scraper for NBC Sports/Rotoworld player news list."""
    try:
        r = requests.get(NBC_PLAYER_NEWS, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")
        items = []
        for a in soup.select('a[href*="/fantasy/football/"]')[:limit]:
            headline = a.get_text(strip=True)
            href = a.get('href')
            if headline and href:
                items.append({"headline": headline, "url": href, "source": "nbc_rotoworld"})
        return items
    except Exception as e:
        return []
