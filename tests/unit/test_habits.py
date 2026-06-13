import pytest
from datetime import date, timedelta
from src.habits import Habit

def test_habit_initialization():
    habit = Habit("Exercise", "adopt", "💪")
    assert habit.name == "Exercise"
    assert habit.completions == []
    assert habit.habit_type == "adopt"

def test_habit_to_dict():
    habit = Habit("Exercise", "adopt", "💪", ["2026-06-09"])
    expected = {
        "name": "Exercise",
        "habit_type": "adopt",
        "category": "health",
        "emoji": "💪",
        "completions": ["2026-06-09"],
        "created_at": date.today().isoformat()
    }
    assert habit.to_dict() == expected

def test_habit_from_dict():
    data = {
        "name": "Exercise",
        "habit_type": "adopt",
        "emoji": "💪",
        "completions": ["2026-06-09"],
        "created_at": "2026-06-01"
    }
    habit = Habit.from_dict(data)
    assert habit.name == "Exercise"
    assert habit.habit_type == "adopt"
    assert habit.completions == ["2026-06-09"]
    assert habit.created_at == "2026-06-01"

def test_mark_complete():
    habit = Habit("Exercise", "adopt", "💪")
    today = date.today().isoformat()
    assert habit.mark_complete() is True
    assert today in habit.completions
    # Duplicate completion same day should return False
    assert habit.mark_complete() is False
    assert len(habit.completions) == 1

def test_current_streak_calculation():
    habit = Habit("Exercise", "adopt", "💪")
    today = date.today()
    yesterday = today - timedelta(days=1)
    day_before = today - timedelta(days=2)
    
    # Empty
    assert habit.get_current_streak() == 0
    
    # Only today
    habit.completions.append(today.isoformat())
    assert habit.get_current_streak() == 1
    
    # Today and yesterday
    habit.completions.append(yesterday.isoformat())
    assert habit.get_current_streak() == 2
    
    # Today, yesterday and day before
    habit.completions.append(day_before.isoformat())
    assert habit.get_current_streak() == 3
    
    # Break streak (remove yesterday)
    habit.completions.remove(yesterday.isoformat())
    assert habit.get_current_streak() == 1 # Only today remains

def test_longest_streak_calculation():
    habit = Habit("Exercise", "adopt", "💪")
    today = date.today()
    yesterday = today - timedelta(days=1)
    day_before = today - timedelta(days=2)
    
    assert habit.get_longest_streak() == 0
    
    habit.completions.append(today.isoformat())
    assert habit.get_longest_streak() == 1
    
    habit.completions.append(yesterday.isoformat())
    assert habit.get_longest_streak() == 2
    
    # Broken streak
    habit.completions.append(day_before.isoformat())
    assert habit.get_longest_streak() == 3
    
    # Separate streaks
    four_days_ago = today - timedelta(days=4)
    five_days_ago = today - timedelta(days=5)
    habit.completions.extend([four_days_ago.isoformat(), five_days_ago.isoformat()])
    assert habit.get_longest_streak() == 3

def test_delete_habit():
    from src.habits import delete_habit
    h1 = Habit("H1", "adopt", "1️⃣")
    h2 = Habit("H2", "adopt", "2️⃣")
    habits = [h1, h2]
    
    assert delete_habit(habits, "H1") is True
    assert len(habits) == 1
    assert habits[0].name == "H2"
    
    # Delete non-existent
    assert delete_habit(habits, "H3") is False
    assert len(habits) == 1


