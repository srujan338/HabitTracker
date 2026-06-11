import json
import os
from typing import List

DATA_FILE = "data/habits.json"


def load_habits() -> List[dict]:
    if not os.path.exists(DATA_FILE):
        os.makedirs("data", exist_ok=True)
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_habits(habits_data: List[dict]) -> None:
    os.makedirs("data", exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(habits_data, f, indent=2, ensure_ascii=False)
