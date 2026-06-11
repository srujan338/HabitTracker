"""
=============================================================================
HABITS MODULE - Core Business Logic
=============================================================================
This module defines the Habit data model and provides functions for
managing habits (create, delete, track completions).

The Habit class is the central data structure that represents a single
habit being tracked. It handles:
- Storing habit metadata (name, emoji, type)
- Tracking completion dates
- Calculating statistics (streaks, rates, ranks)

Data Flow:
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  main.py        │────▶│  Habit Class     │────▶│  storage.py     │
│  (UI Layer)     │     │  (Business Logic)│     │  (Data Layer)   │
└─────────────────┘     └──────────────────┘     └─────────────────┘

Key Concepts:
- Streak: Consecutive days of completion (current and longest)
- Completion Rate: Percentage of days habit was completed
- Rank: Gamified level based on streak length
=============================================================================
"""

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Optional


# ═══════════════════════════════════════════════════════════════════════════
# HABIT DATA MODEL
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class Habit:
    """
    Represents a single habit being tracked.
    
    A habit is defined by:
    - name: Human-readable identifier (e.g., "Morning Meditation")
    - habit_type: Either "adopt" (start doing) or "quit" (stop doing)
    - emoji: Visual icon for quick recognition
    - completions: List of ISO date strings when habit was completed
    - created_at: Date when the habit was first created
    
    The dataclass decorator auto-generates __init__, __repr__, etc.
    
    Example:
        >>> habit = Habit(name="Exercise", habit_type="adopt", emoji="🏃")
        >>> habit.mark_complete()
        >>> print(habit.get_current_streak())  # 1
    """
    
    # ── Required Fields ────────────────────────────────────────────────────
    name: str
    """Human-readable name for the habit (e.g., 'Read 10 pages')"""
    
    habit_type: str
    """Type of habit: 'adopt' (build) or 'quit' (break)"""
    
    emoji: str
    """Visual icon for the habit (e.g., '📚', '🏃')"""
    
    # ── Optional Fields with Defaults ──────────────────────────────────────
    completions: List[str] = field(default_factory=list)
    """List of ISO format date strings (e.g., ['2024-01-15', '2024-01-16'])"""
    
    created_at: str = field(default_factory=lambda: date.today().isoformat())
    """Date when the habit was created (ISO format)"""
    
    # ── Derived Statistics Methods ─────────────────────────────────────────
    # These methods calculate values from the completion data.
    
    def is_completed_today(self) -> bool:
        """
        Check if the habit was completed today.
        
        Returns:
            True if today's date is in the completions list
            
        Example:
            >>> habit.is_completed_today()
            False
            >>> habit.mark_complete()
            >>> habit.is_completed_today()
            True
        """
        return date.today().isoformat() in self.completions
    
    def get_current_streak(self) -> int:
        """
        Calculate the current consecutive day streak.
        
        A streak is the number of consecutive days (including today or
        yesterday) where the habit was completed. If today is not yet
        completed, we check if yesterday was, to avoid breaking streaks
        for habits not yet done today.
        
        Algorithm:
        1. Start from today (or yesterday if today not completed)
        2. Count backwards while each day exists in completions
        3. Stop at first missing day
        
        Returns:
            Number of consecutive days (0 if no streak)
            
        Example:
            If habit was completed on Jan 10, 11, 12, 13, 14:
            >>> habit.get_current_streak()  # Returns 5
        """
        if not self.completions:
            return 0
        
        # Sort completions in descending order (most recent first)
        sorted_dates = sorted(self.completions, reverse=True)
        
        streak = 0
        today = date.today()
        
        # Check if today is completed
        if today.isoformat() in sorted_dates:
            check_date = today
        # Check if yesterday is completed (streak continues if today not done yet)
        elif (today - timedelta(days=1)).isoformat() in sorted_dates:
            check_date = today - timedelta(days=1)
        else:
            return 0  # No active streak
        
        # Count consecutive days backwards
        for d_str in sorted_dates:
            if d_str == check_date.isoformat():
                streak += 1
                check_date -= timedelta(days=1)
            elif d_str == (check_date + timedelta(days=1)).isoformat():
                # Today not yet checked, skip
                continue
            else:
                # Gap found, streak broken
                break
        
        return streak
    
    def get_longest_streak(self) -> int:
        """
        Find the longest streak ever achieved for this habit.
        
        Unlike get_current_streak(), this looks at all historical data
        to find the best streak, even if it's not active now.
        
        Algorithm:
        1. Convert all completion strings to date objects
        2. Sort dates chronologically
        3. Iterate through, counting consecutive sequences
        4. Track the maximum length found
        
        Returns:
            Length of longest streak (0 if no completions)
            
        Example:
            Completions: Jan 1-5 (5 days), Jan 10-15 (6 days)
            >>> habit.get_longest_streak()  # Returns 6
        """
        if not self.completions:
            return 0
        
        # Convert strings to date objects, filtering invalid entries
        valid_dates = []
        for d_str in self.completions:
            try:
                valid_dates.append(date.fromisoformat(d_str))
            except (ValueError, TypeError):
                # Skip malformed dates (defensive programming)
                continue
        
        if not valid_dates:
            return 0
        
        # Sort chronologically
        sorted_dates = sorted(valid_dates)
        
        longest = current = 1
        
        # Count consecutive sequences
        for i in range(1, len(sorted_dates)):
            prev_date = sorted_dates[i - 1]
            curr_date = sorted_dates[i]
            
            # Check if dates are consecutive (1 day apart)
            if (curr_date - prev_date).days == 1:
                current += 1
                longest = max(longest, current)
            else:
                # Reset counter on gap
                current = 1
        
        return longest
    
    def get_total_completions(self) -> int:
        """
        Count total number of times the habit was completed.
        
        This is a simple count of all entries in the completions list,
        regardless of dates or streaks.
        
        Returns:
            Total number of completion records
            
        Example:
            >>> habit.get_total_completions()
            42
        """
        return len(self.completions)
    
    def get_completion_rate(self, days: int = 30) -> float:
        """
        Calculate completion percentage over a time period.
        
        This measures consistency: what percentage of days in the
        given period was the habit completed?
        
        Args:
            days: Number of days to look back (default: 30)
        
        Returns:
            Percentage (0.0 to 100.0) of days completed
            
        Example:
            If habit was completed 15 out of last 30 days:
            >>> habit.get_completion_rate(30)  # Returns 50.0
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=days - 1)
        
        # Filter valid completions within the date range
        completed_count = 0
        for d_str in self.completions:
            try:
                d = date.fromisoformat(d_str)
                if start_date <= d <= end_date:
                    completed_count += 1
            except (ValueError, TypeError):
                continue
        
        # Calculate actual number of days habit could have been done
        try:
            created = date.fromisoformat(self.created_at)
        except (ValueError, TypeError):
            created = date.today()
        
        # Days since creation (or start of period, whichever is later)
        effective_start = max(start_date, created)
        actual_days = (end_date - effective_start).days + 1
        
        # Avoid division by zero
        if actual_days <= 0:
            return 0.0
        
        return round((completed_count / actual_days) * 100, 1)
    
    def get_rank(self) -> dict:
        """
        Get the current rank/badge based on streak length.
        
        Ranks provide gamification - users work to "level up" their
        habits by maintaining longer streaks.
        
        Rank Tiers:
        - Not Started (< 1 day): Just beginning
        - Starter (1-2 days): Taking first steps
        - Bronze (3-6 days): Building momentum
        - Silver (7-13 days): Forming a habit
        - Gold (14-29 days): Strong commitment
        - Legend (30+ days): Habit master
        
        Returns:
            Dictionary with rank metadata:
            - label: Rank name
            - color: Hex color code
            - bg: Background color (rgba)
            - icon: Emoji badge
            
        Example:
            >>> habit.get_rank()
            {'label': 'Bronze', 'color': '#CD7F32', 'icon': '🥉', ...}
        """
        streak = self.get_current_streak()
        
        if streak >= 30:
            return {
                "label": "Legend",
                "color": "#F5A623",
                "bg": "rgba(245, 166, 35, 0.12)",
                "icon": "🏅"
            }
        elif streak >= 14:
            return {
                "label": "Gold",
                "color": "#FFD700",
                "bg": "rgba(255, 215, 0, 0.12)",
                "icon": "🥇"
            }
        elif streak >= 7:
            return {
                "label": "Silver",
                "color": "#A8B8C8",
                "bg": "rgba(168, 184, 200, 0.15)",
                "icon": "🥈"
            }
        elif streak >= 3:
            return {
                "label": "Bronze",
                "color": "#CD7F32",
                "bg": "rgba(205, 127, 50, 0.15)",
                "icon": "🥉"
            }
        elif streak >= 1:
            return {
                "label": "Starter",
                "color": "#4ECDC4",
                "bg": "rgba(78, 205, 196, 0.12)",
                "icon": "🌱"
            }
        else:
            return {
                "label": "Not started",
                "color": "#94A3B8",
                "bg": "rgba(148, 163, 184, 0.08)",
                "icon": "—"
            }
    
    def get_calendar_month(self, year: int, month: int) -> dict:
        """
        Get completion status for each day in a specific month.
        
        Used for rendering calendar views that show which days
        the habit was completed.
        
        Args:
            year: Four-digit year (e.g., 2024)
            month: Month number (1-12)
        
        Returns:
            Dictionary mapping day number to True if completed
            Example: {1: True, 2: True, 3: False, 5: True, ...}
            
        Example:
            >>> habit.get_calendar_month(2024, 1)
            {1: True, 2: True, 3: False, 4: True, ...}
        """
        result = {}
        for d_str in self.completions:
            try:
                d = date.fromisoformat(d_str)
                if d.year == year and d.month == month:
                    result[d.day] = True
            except (ValueError, TypeError):
                continue
        return result
    
    def mark_complete(self) -> bool:
        """
        Mark the habit as completed for today.
        
        This is the primary action users take when they complete
        their habit for the day.
        
        Returns:
            True if successfully marked (wasn't already done today)
            False if already completed today (no duplicate entries)
            
        Example:
            >>> habit.mark_complete()
            True
            >>> habit.mark_complete()  # Already done
            False
        """
        today = date.today().isoformat()
        if today not in self.completions:
            self.completions.append(today)
            return True
        return False
    
    # ── Serialization Methods ──────────────────────────────────────────────
    # These methods convert between Habit objects and dictionaries
    # for storage in JSON format.
    
    def to_dict(self) -> dict:
        """
        Convert Habit object to a dictionary for JSON serialization.
        
        Returns:
            Dictionary with all habit data
            
        Example:
            >>> habit.to_dict()
            {
                'name': 'Exercise',
                'habit_type': 'adopt',
                'emoji': '🏃',
                'completions': ['2024-01-15', '2024-01-16'],
                'created_at': '2024-01-15'
            }
        """
        return {
            "name": self.name,
            "habit_type": self.habit_type,
            "emoji": self.emoji,
            "completions": self.completions,
            "created_at": self.created_at,
        }
    
    @classmethod
    def from_dict(cls, d: dict) -> "Habit":
        """
        Create a Habit object from a dictionary (reverse of to_dict).
        
        This method also validates and cleans the data:
        - Ensures completions are strings
        - Provides defaults for missing fields
        - Handles malformed data gracefully
        
        Args:
            d: Dictionary with habit data
        
        Returns:
            New Habit instance
            
        Example:
            >>> data = {'name': 'Reading', 'habit_type': 'adopt', ...}
            >>> habit = Habit.from_dict(data)
        """
        # Validate and clean completions list
        raw_completions = d.get("completions", [])
        valid_completions = [
            c for c in raw_completions 
            if isinstance(c, str)
        ]
        
        return cls(
            name=d.get("name", "Unnamed Habit"),
            habit_type=d.get("habit_type", "adopt"),
            emoji=d.get("emoji", "✅"),
            completions=valid_completions,
            created_at=d.get("created_at", date.today().isoformat()),
        )


# ═══════════════════════════════════════════════════════════════════════════
# HABIT MANAGEMENT FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def add_habit(habits: List[Habit], name: str, habit_type: str, emoji: str) -> tuple:
    """
    Create a new habit and add it to the habits list.
    
    This function validates the input and ensures no duplicate
    habit names exist (case-insensitive comparison).
    
    Args:
        habits: List of existing habits to add to
        name: Name for the new habit
        habit_type: Either "adopt" or "quit"
        emoji: Icon for the habit
    
    Returns:
        Tuple of (Habit object, error message)
        - On success: (Habit, None)
        - On failure: (None, "error message")
    
    Example:
        >>> habit, error = add_habit(habits, "Meditation", "adopt", "🧘")
        >>> if error:
        ...     print(f"Failed: {error}")
        ... else:
        ...     print(f"Created: {habit.name}")
    """
    # Check for duplicate names (case-insensitive)
    if any(h.name.lower() == name.lower() for h in habits):
        return None, "A habit with that name already exists."
    
    # Create and add the new habit
    habit = Habit(name=name, habit_type=habit_type, emoji=emoji)
    habits.append(habit)
    
    return habit, None


def delete_habit(habits: List[Habit], name: str) -> bool:
    """
    Remove a habit from the habits list.
    
    WARNING: This permanently deletes all completion history
    for the habit. Consider adding a confirmation step in the UI.
    
    Args:
        habits: List of habits to remove from
        name: Name of the habit to delete
    
    Returns:
        True if habit was found and deleted
        False if habit was not found
    
    Example:
        >>> delete_habit(habits, "Old Habit")
        True
        >>> delete_habit(habits, "Non-existent")
        False
    """
    for i, h in enumerate(habits):
        if h.name == name:
            habits.pop(i)
            return True
    return False