import pytest
from datetime import date, timedelta
from src.habits import Habit

def test_habit_initialization():
    habit = Habit("Exercise")
    assert habit.name == "Exercise"
    assert habit.completions == []
    assert habit.longest_streak == 0

def test_habit_to_dict():
    habit = Habit("Exercise", ["2026-06-09"], 1)
    expected = {
        "name": "Exercise",
        "completions": ["2026-06-09"],
        "longest_streak": 1
    }
    assert habit.to_dict() == expected

def test_habit_from_dict():
    data = {
        "name": "Exercise",
        "completions": ["2026-06-09"],
        "longest_streak": 1
    }
    habit = Habit.from_dict(data)
    assert habit.name == "Exercise"
    assert habit.completions == ["2026-06-09"]
    assert habit.longest_streak == 1

def test_mark_complete():
    habit = Habit("Exercise")
    today = date.today().isoformat()
    assert habit.mark_complete() is True
    assert today in habit.completions
    # Duplicate completion same day should return False
    assert habit.mark_complete() is False
    assert len(habit.completions) == 1

def test_current_streak_calculation():
    habit = Habit("Exercise")
    today = date.today()
    yesterday = today - timedelta(days=1)
    day_before = today - timedelta(days=2)
    
    # Empty
    assert habit.get_current_streak() == 0
    
    # Only today
    habit.mark_complete(today.isoformat())
    assert habit.get_current_streak() == 1
    
    # Today and yesterday
    habit.mark_complete(yesterday.isoformat())
    assert habit.get_current_streak() == 2
    
    # Today, yesterday and day before
    habit.mark_complete(day_before.isoformat())
    assert habit.get_current_streak() == 3
    
    # Break streak (remove yesterday)
    habit.completions.remove(yesterday.isoformat())
    assert habit.get_current_streak() == 1 # Only today remains

def test_longest_streak_update():
    habit = Habit("Exercise")
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    assert habit.update_longest_streak() == 0
    
    habit.mark_complete(today.isoformat())
    assert habit.update_longest_streak() == 1
    assert habit.longest_streak == 1
    
    habit.mark_complete(yesterday.isoformat())
    assert habit.update_longest_streak() == 2
    assert habit.longest_streak == 2
    
    # Broken streak shouldn't decrease longest_streak
    habit.completions = [today.isoformat()]
    assert habit.get_current_streak() == 1
    assert habit.update_longest_streak() == 2
    assert habit.longest_streak == 2

def test_delete_habit():
    from src.habits import delete_habit
    h1 = Habit("H1")
    h2 = Habit("H2")
    habits = [h1, h2]
    
    assert delete_habit(habits, "H1") is True
    assert len(habits) == 1
    assert habits[0].name == "H2"
    
    # Delete non-existent
    assert delete_habit(habits, "H3") is False
    assert len(habits) == 1


