"""
Habits module for the Habit Tracker application.
Contains the Habit class and helper functions for habit management.
"""

from datetime import datetime, date, timedelta


class Habit:
    """
    Represents a recurring task that a user wants to track.
    """

    def __init__(self, name, completions=None, longest_streak=0):
        """
        Initialize a new Habit instance.

        Args:
            name (str): The unique name of the habit.
            completions (list, optional): List of ISO-8601 date strings.
            longest_streak (int, optional): The recorded longest streak.
        """
        self.name = name
        self.completions = completions if completions is not None else []
        self.longest_streak = longest_streak

    @classmethod
    def from_dict(cls, data):
        """
        Create a Habit instance from a dictionary.

        Args:
            data (dict): Dictionary containing habit attributes.

        Returns:
            Habit: A new Habit instance.
        """
        return cls(
            name=data["name"],
            completions=data.get("completions", []),
            longest_streak=data.get("longest_streak", 0),
        )

    def to_dict(self):
        """
        Convert the Habit instance to a dictionary.

        Returns:
            dict: Dictionary representation of the habit.
        """
        return {
            "name": self.name,
            "completions": self.completions,
            "longest_streak": self.longest_streak,
        }

    def mark_complete(self, completion_date=None):
        """
        Mark the habit as complete for a given date.

        Args:
            completion_date (str, optional): ISO-8601 date string. Defaults to today.

        Returns:
            bool: True if completion was added, False if already exists.
        """
        if completion_date is None:
            completion_date = date.today().isoformat()

        if completion_date not in self.completions:
            self.completions.append(completion_date)
            self.completions.sort()
            # Update longest streak whenever a new completion is added
            self.update_longest_streak()
            return True
        return False

    def get_current_streak(self):
        """
        Calculate the current streak based on completions.

        Returns:
            int: Number of consecutive days completed up to today or yesterday.
        """
        if not self.completions:
            return 0

        # Sort completions descending (newest first)
        sorted_dates = sorted(
            [datetime.strptime(d, "%Y-%m-%d").date() for d in self.completions],
            reverse=True,
        )

        today = date.today()

        # If the most recent completion is older than yesterday, the streak is 0
        last_date = sorted_dates[0]
        if last_date < today - timedelta(days=1):
            return 0

        streak = 1
        for i in range(len(sorted_dates) - 1):
            if sorted_dates[i] - sorted_dates[i + 1] == timedelta(days=1):
                streak += 1
            else:
                break
        return streak

    def update_longest_streak(self):
        """
        Update the longest streak record if current streak is higher.

        Returns:
            int: The updated longest streak.
        """
        current = self.get_current_streak()
        if current > self.longest_streak:
            self.longest_streak = current
        return self.longest_streak


def add_habit(habits_list, name):
    """
    Add a new habit to the list if the name is unique.

    Args:
        habits_list (list): List of Habit instances.
        name (str): The name of the new habit.

    Returns:
        tuple: (Habit or None, error_message or None)
    """
    if any(h.name.lower() == name.lower() for h in habits_list):
        return None, "Habit with this name already exists."

    new_habit = Habit(name)
    habits_list.append(new_habit)
    return new_habit, None


def delete_habit(habits_list, name):
    """
    Remove a habit from the list by name.

    Args:
        habits_list (list): List of Habit instances.
        name (str): The name of the habit to remove.

    Returns:
        bool: True if habit was found and removed, False otherwise.
    """
    for i, h in enumerate(habits_list):
        if h.name == name:
            habits_list.pop(i)
            return True
    return False
