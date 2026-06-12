"""
=============================================================================
STORAGE MODULE - Supabase Persistence Layer
=============================================================================
This module handles all data persistence operations using Supabase (PostgreSQL).

Responsibilities:
- Loading habit data from Supabase
- Saving/Upserting habit data to Supabase
- Handling database errors gracefully

Data Structure:
Habits are stored in the 'habits' table in Supabase.
=============================================================================
"""

import json
import os
from typing import List
from src.supabase_client import supabase

DATA_FILE = "data/habits.json"

def load_habits(username: str = None) -> List[dict]:
    """Load habits from JSON test storage or Supabase user storage."""
    if username is None:
        return _load_habits_json()

    try:
        response = supabase.table("habits").select("*").eq("user_id", username).execute()
        return response.data
    except Exception as e:
        print(f"Error loading habits from Supabase: {e}")
        return []

def save_habits(habits: List[dict]) -> None:
    """Save all habits to the local JSON file for tests/local fallback."""
    directory = os.path.dirname(DATA_FILE)
    if directory:
        os.makedirs(directory, exist_ok=True)

    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(habits, file, indent=2)

def save_habit(username: str, habit_data: dict) -> None:
    """Save or update a habit in Supabase without relying on upsert."""
    try:
        data = {**habit_data, "user_id": username}
        try:
            supabase.table("habits").insert(data).execute()
        except Exception as insert_exc:
            msg = str(insert_exc)
            if "duplicate key value violates unique constraint" in msg:
                supabase.table("habits").update(data).eq("user_id", username).eq("name", data.get("name")).execute()
            else:
                raise
    except Exception as e:
        print(f"Error saving habit to Supabase: {e}")
        raise

def delete_habit(user_id: str, habit_name: str) -> bool:
    """
    Remove a habit from Supabase.
    
    Args:
        user_id: The UUID of the user.
        habit_name: The name of the habit to delete.
        
    Returns:
        True if successful.
    """
    try:
        supabase.table("habits").delete().eq("user_id", user_id).eq("name", habit_name).execute()
        return True
    except Exception as e:
        print(f"Error deleting habit from Supabase: {e}")
        return False

def _load_habits_json() -> List[dict]:
    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []
