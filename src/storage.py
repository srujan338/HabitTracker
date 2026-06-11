"""
=============================================================================
STORAGE MODULE - Data Persistence Layer
=============================================================================
This module handles all data persistence operations, now using MongoDB Atlas.

Responsibilities:
- Loading habit data from MongoDB
- Saving habit data to MongoDB
- Handling database errors gracefully

Data Structure:
Habits are stored in the 'habits' collection.
Each habit document:
{
    "_id": ObjectId(...),
    "username": "srujan",
    "name": "Morning Meditation",
    "habit_type": "adopt",
    "emoji": "🧘",
    "completions": ["2024-01-15", "2024-01-16"],
    "created_at": "2024-01-15"
}
=============================================================================
"""

from typing import List, Optional
from src.database import get_collection
from bson import ObjectId

# Collection names
HABITS_COLLECTION = "habits"

def load_habits(username: str) -> List[dict]:
    """
    Load habits for a specific user from MongoDB.
    
    Args:
        username: The username of the user to load habits for.
        
    Returns:
        List of habit dictionaries.
    """
    collection = get_collection(HABITS_COLLECTION)
    habits = list(collection.find({"username": username}))
    
    # Convert MongoDB _id to string for compatibility
    for habit in habits:
        habit["_id"] = str(habit["_id"])
    
    return habits

def save_habits(username: str, habits_data: List[dict]) -> None:
    """
    Save habit data to MongoDB, replacing the user's current habits.
    
    Args:
        username: The username to save habits for.
        habits_data: List of habit dictionaries to save.
    """
    collection = get_collection(HABITS_COLLECTION)
    
    # For simplicity in this implementation, we delete existing habits for user
    # and re-insert the updated list.
    collection.delete_many({"username": username})
    
    if habits_data:
        # Add username to each habit document
        for habit in habits_data:
            habit["username"] = username
            # Remove _id if present, as it will be re-generated
            if "_id" in habit:
                del habit["_id"]
        
        collection.insert_many(habits_data)
