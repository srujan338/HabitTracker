"""
=============================================================================
STORAGE MODULE - Data Persistence Layer
=============================================================================
This module handles all data persistence operations, providing a clean
separation between the application logic and file system operations.

Responsibilities:
- Loading habit data from JSON file on startup
- Saving habit data to JSON file after modifications
- Creating necessary directories if they don't exist
- Handling file I/O errors gracefully

Data Format:
The habits are stored in a JSON file with the following structure:

[
    {
        "name": "Morning Meditation",
        "habit_type": "adopt",
        "emoji": "🧘",
        "completions": ["2024-01-15", "2024-01-16", "2024-01-17"],
        "created_at": "2024-01-15"
    },
    {
        "name": "Exercise",
        "habit_type": "adopt",
        "emoji": "🏃",
        "completions": ["2024-01-15", "2024-01-16"],
        "created_at": "2024-01-15"
    }
]

Design Principles:
1. Fail gracefully: Return empty list on read errors, don't crash
2. Create directories: Auto-create data directory if missing
3. UTF-8 encoding: Support international characters in habit names
4. Pretty printing: Use indentation for human-readable JSON
=============================================================================
"""

import json
import os
from typing import List
from datetime import date


# ── Configuration ──────────────────────────────────────────────────────────

# Default location for the habits database file
# Using a relative path keeps the project self-contained
DATA_FILE = "data/habits.json"


# ── Data Access Functions ──────────────────────────────────────────────────

def load_habits() -> List[dict]:
    """
    Load habits data from the JSON file.
    
    This function is called at application startup to restore the
    user's habit data from persistent storage.
    
    Behavior on errors:
    - File not found: Creates the data directory and returns empty list
    - Invalid JSON: Returns empty list (data corruption recovery)
    - Permission errors: Returns empty list (graceful degradation)
    
    Returns:
        List of habit dictionaries, or empty list if file doesn't exist
        or is invalid
        
    Example:
        >>> habits = load_habits()
        >>> print(len(habits))
        3
        >>> print(habits[0]['name'])
        'Morning Meditation'
    """
    # Check if file exists
    if not os.path.exists(DATA_FILE):
        # Create the data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)
        # Return empty list (no habits yet)
        return []
    
    try:
        # Open and read the JSON file
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Validate that we got a list
        if not isinstance(data, list):
            print(f"Warning: Expected list in {DATA_FILE}, got {type(data).__name__}")
            return []
        
        return data
        
    except json.JSONDecodeError as e:
        # JSON file is corrupted
        print(f"Warning: JSON decode error in {DATA_FILE}: {e}")
        # Could backup the corrupted file here
        return []
        
    except IOError as e:
        # File read error (permissions, etc.)
        print(f"Warning: Could not read {DATA_FILE}: {e}")
        return []
    
    except Exception as e:
        # Catch any other unexpected errors
        print(f"Warning: Unexpected error loading habits: {e}")
        return []


def save_habits(habits_data: List[dict]) -> None:
    """
    Save habits data to the JSON file.
    
    This function is called after any modification to habit data
    (creating, deleting, or completing habits) to persist changes.
    
    Features:
    - Creates data directory if it doesn't exist
    - Uses pretty-printing (indent=2) for human readability
    - Preserves Unicode characters (emoji, international text)
    - Atomic-ish write (writes to temp then renames would be better)
    
    Args:
        habits_data: List of habit dictionaries to save
        
    Raises:
        IOError: If the file cannot be written (permissions, disk full, etc.)
        
    Example:
        >>> habits = [
        ...     {"name": "Exercise", "emoji": "🏃", ...}
        ... ]
        >>> save_habits(habits)
        # Data is now persisted to data/habits.json
    """
    # Ensure the data directory exists
    os.makedirs("data", exist_ok=True)
    
    try:
        # Write to a temporary file first, then rename for atomicity
        temp_file = DATA_FILE + ".tmp"
        
        with open(temp_file, "w", encoding="utf-8") as f:
            # json.dump parameters:
            # - indent=2: Pretty print with 2-space indentation
            # - ensure_ascii=False: Preserve emoji and international characters
            json.dump(habits_data, f, indent=2, ensure_ascii=False)
        
        # Atomic rename (on most systems)
        os.replace(temp_file, DATA_FILE)
        
    except IOError as e:
        # Handle write errors
        print(f"Error: Could not save habits to {DATA_FILE}: {e}")
        # Clean up temp file if it exists
        if os.path.exists(DATA_FILE + ".tmp"):
            try:
                os.remove(DATA_FILE + ".tmp")
            except OSError:
                pass
        raise
    
    except Exception as e:
        print(f"Error: Unexpected error saving habits: {e}")
        raise


# ── Utility Functions ──────────────────────────────────────────────────────

def get_data_file_path() -> str:
    """
    Get the absolute path to the data file.
    
    Useful for debugging or when you need the full path.
    
    Returns:
        Absolute path to the habits JSON file
        
    Example:
        >>> get_data_file_path()
        '/home/user/studytracker/data/habits.json'
    """
    return os.path.abspath(DATA_FILE)


def backup_habits(backup_name: str = None) -> str:
    """
    Create a backup of the current habits file.
    
    Useful before major operations or for version control.
    
    Args:
        backup_name: Optional name for the backup file.
                    If None, uses timestamp-based naming.
    
    Returns:
        Path to the backup file, or None if backup failed
        
    Example:
        >>> backup_path = backup_habits("before_cleanup")
        >>> print(f"Backup saved to: {backup_path}")
    """
    if not os.path.exists(DATA_FILE):
        return None
    
    if backup_name is None:
        # Generate timestamp-based name
        timestamp = date.today().isoformat()
        backup_name = f"habits_backup_{timestamp}.json"
    elif not backup_name.endswith(".json"):
        backup_name += ".json"
    
    backup_path = os.path.join("data", backup_name)
    
    try:
        import shutil
        shutil.copy2(DATA_FILE, backup_path)
        return backup_path
    except (IOError, shutil.Error) as e:
        print(f"Warning: Could not create backup: {e}")
        return None


def get_storage_stats() -> dict:
    """
    Get statistics about the storage file.
    
    Useful for debugging and monitoring.
    
    Returns:
        Dictionary with storage statistics
        
    Example:
        >>> stats = get_storage_stats()
        >>> print(stats['file_size'])
        '1.2 KB'
    """
    stats = {
        "file_exists": os.path.exists(DATA_FILE),
        "file_path": get_data_file_path(),
        "file_size": "0 B",
        "last_modified": None,
    }
    
    if stats["file_exists"]:
        stat = os.stat(DATA_FILE)
        size = stat.st_size
        
        # Format file size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                stats["file_size"] = f"{size:.1f} {unit}"
                break
            size /= 1024.0
        
        # Format last modified time
        from datetime import datetime
        stats["last_modified"] = datetime.fromtimestamp(stat.st_mtime).isoformat()
    
    return stats


# ── Context Manager for Safe File Operations ──────────────────────────────

class HabitStorage:
    """
    Context manager for safe habit storage operations.
    
    Provides automatic loading on enter and saving on exit,
    with proper error handling.
    
    Example:
        >>> with HabitStorage() as storage:
        ...     habits = storage.load()
        ...     # Modify habits
        ...     storage.save(habits)
        ...     # Auto-saves on exit
    """
    
    def __init__(self, file_path: str = DATA_FILE):
        self.file_path = file_path
        self.data = []
    
    def __enter__(self):
        self.data = self.load()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:  # No exception occurred
            self.save(self.data)
        return False
    
    def load(self) -> List[dict]:
        """Load habits from the configured file."""
        if not os.path.exists(self.file_path):
            return []
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    
    def save(self, data: List[dict]) -> None:
        """Save habits to the configured file."""
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)