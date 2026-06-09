# Data Model: Habit Tracker

## Entities

### Habit
Represents a recurring task that a user wants to track.

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `name` | string | Unique name of the habit | Required, Unique, non-empty |
| `completions` | list[string] | List of ISO-8601 dates (YYYY-MM-DD) | Unique dates |
| `current_streak` | integer | (Calculated) Current consecutive days | >= 0 |
| `longest_streak` | integer | (Stored/Calculated) Max consecutive days | >= 0 |

## Relationships
- **Single Entity**: The app manages a list of `Habit` objects.
- **No User Entity**: A single-user system is assumed for the MVP.

## JSON Storage Schema
The data is stored as a list of objects in `habits.json`:

```json
[
  {
    "name": "Exercise",
    "completions": ["2026-06-07", "2026-06-08", "2026-06-09"],
    "longest_streak": 3
  },
  {
    "name": "Read",
    "completions": ["2026-06-08"],
    "longest_streak": 1
  }
]
```

## State Transitions
1. **Creation**: New habit initialized with empty completions and 0 streaks.
2. **Completion**: Appends today's date to `completions`. Updates `longest_streak` if necessary.
3. **Deletion**: Habit object is removed from the list.
