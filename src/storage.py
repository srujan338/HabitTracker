"""
Storage module for the Habit Tracker application.
Handles JSON file I/O operations for persistent habit data.
"""

import json
import os

HABITS_FILE = "habits.json"


def load_habits():
    """
    Load habits from the JSON file.

    Returns:
        list: A list of habit dictionaries. Returns an empty list if the file
              does not exist or is corrupted.
    """
    if not os.path.exists(HABITS_FILE):
        return []
    try:
        with open(HABITS_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_habits(habits):
    """
    Save habits to the JSON file.

    Args:
        habits (list): A list of habit dictionaries to persist.

    Returns:
        bool: True if save was successful, False otherwise.
    """
    try:
        with open(HABITS_FILE, "w") as f:
            json.dump(habits, f, indent=4)
        return True
    except IOError:
        return False
