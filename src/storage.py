"""
=============================================================================
STORAGE MODULE - Local JSON Persistence Layer
=============================================================================
This module handles local JSON file storage for habit data.
=============================================================================
"""

import json
import os
from typing import List

DATA_FILE = "data/habits.json"

def load_habits(username: str) -> List[dict]:
    """Load habits for a user from a local JSON file."""
    # Simple JSON implementation for local storage
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            all_data = json.load(f)
            # Filter by username
            return [h for h in all_data if h.get("username") == username]
    except Exception:
        return []

def save_habits(username: str, habits_data: List[dict]) -> None:
    """Save habits for a user to a local JSON file."""
    os.makedirs("data", exist_ok=True)
    
    # Load all, remove user's old habits, add new ones, save all
    all_data = []
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                all_data = json.load(f)
        except:
            all_data = []
            
    # Filter out old habits for this user
    all_data = [h for h in all_data if h.get("username") != username]
    
    # Add new habits
    for habit in habits_data:
        habit["username"] = username
        if "_id" in habit:
            del habit["_id"]
        all_data.append(habit)
        
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)
