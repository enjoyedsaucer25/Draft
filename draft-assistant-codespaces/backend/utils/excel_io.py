# Placeholder for future Excel write/read using openpyxl or xlwings.
# First release focuses on fast local UI with CSV export.
from typing import List, Dict
import csv, os

def export_picks_csv(picks: List[Dict], path: str = "data/picks_export.csv"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not picks:
        return path
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(picks[0].keys()))
        writer.writeheader()
        for row in picks:
            writer.writerow(row)
    return path
