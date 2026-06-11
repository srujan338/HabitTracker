import os
import json
import pytest
from src.storage import load_habits, save_habits, DATA_FILE

@pytest.fixture
def temp_habits_file(tmp_path):
    """Fixture to mock the habits file in a temporary directory."""
    original_file = DATA_FILE
    temp_file = tmp_path / "habits.json"
    
    # Monkeypatch the DATA_FILE in storage module
    import src.storage
    src.storage.DATA_FILE = str(temp_file)
    
    yield temp_file
    
    # Restore the original DATA_FILE
    src.storage.DATA_FILE = original_file

def test_load_habits_no_file(temp_habits_file):
    """Test loading habits when the file doesn't exist."""
    assert load_habits() == []

def test_save_and_load_habits(temp_habits_file):
    """Test saving and then loading habits."""
    test_data = [
        {"name": "Exercise", "habit_type": "adopt", "emoji": "💪", "completions": ["2026-06-07"], "created_at": "2026-06-01"}
    ]
    save_habits(test_data)
    assert load_habits() == test_data

def test_load_habits_corrupt_file(temp_habits_file):
    """Test loading habits from a corrupt JSON file."""
    # Ensure data dir exists
    os.makedirs(os.path.dirname(temp_habits_file), exist_ok=True)
    with open(temp_habits_file, "w") as f:
        f.write("not json")
    assert load_habits() == []

def test_habit_persistence_flow(temp_habits_file):
    """Test the full flow of creating a habit, saving it, and reloading it."""
    from src.habits import Habit
    
    # 1. Start empty
    habits = []
    
    # 2. Create new habit
    new_habit = Habit("Read", "adopt", "📚")
    habits.append(new_habit.to_dict())
    
    # 3. Save
    save_habits(habits)
    
    # 4. Reload
    reloaded_data = load_habits()
    assert len(reloaded_data) == 1
    assert reloaded_data[0]["name"] == "Read"

def test_delete_and_save_flow(temp_habits_file):
    """Test deleting a habit and verifying storage is updated."""
    from src.habits import Habit, delete_habit
    
    # 1. Setup with 2 habits
    habits = [Habit("H1", "adopt", "1️⃣"), Habit("H2", "adopt", "2️⃣")]
    save_habits([h.to_dict() for h in habits])
    
    # 2. Delete H1
    assert delete_habit(habits, "H1") is True
    
    # 3. Save
    save_habits([h.to_dict() for h in habits])
    
    # 4. Reload and verify
    reloaded = load_habits()
    assert len(reloaded) == 1
    assert reloaded[0]["name"] == "H2"


