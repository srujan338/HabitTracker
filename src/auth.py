"""
=============================================================================
AUTH MODULE - User Authentication & Profile Management
=============================================================================
This module handles user authentication, profile management, and 
gamification features including:
- User registration and login
- XP (experience points) and leveling system
- User parameters/stats (discipline, consistency, etc.)
- Global rankings
- Achievements and badges

Data Model:
┌─────────────────────────────────────────────────────────────┐
│  User Profile                                                │
├─────────────────────────────────────────────────────────────┤
│  - username, password (hashed)                               │
│  - level, xp, xp_to_next_level                               │
│  - parameters: discipline, consistency, dedication           │
│  - global_rank, total_streak_days                            │
│  - achievements, joined_events                               │
│  - created_at, last_active                                   │
└─────────────────────────────────────────────────────────────┘

Gamification System:
- XP earned from completing habits (10 XP per completion)
- Bonus XP for streaks (streak_multiplier)
- Level up every 100 XP (exponential scaling)
- Parameters improve based on user behavior
=============================================================================
"""

import json
import os
import hashlib
from datetime import date, timedelta
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field, asdict


# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

USERS_FILE = "data/users.json"

# XP required for each level (level * 100)
XP_PER_LEVEL = 100

# XP rewards
XP_HABIT_COMPLETION = 10
XP_STREAK_BONUS = 5  # Bonus per streak day
XP_EVENT_COMPLETION = 25

# User parameters range
PARAM_MIN = 1
PARAM_MAX = 100


# ═══════════════════════════════════════════════════════════════════════════
# USER DATA MODEL
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class User:
    """
    Represents a user with gamification features.
    
    Attributes:
        username: Unique username
        password_hash: SHA-256 hash of password
        level: Current user level (starts at 1)
        xp: Current experience points
        parameters: User stats (discipline, consistency, etc.)
        global_rank: Position in global leaderboard
        total_streak_days: Sum of all streak days across habits
        achievements: List of earned achievement IDs
        joined_events: List of event IDs user has joined
        completed_events: List of event IDs user has completed
        created_at: Account creation date
        last_active: Last activity date
    """
    username: str
    password_hash: str
    
    # Gamification
    level: int = 1
    xp: int = 0
    title: str = "Beginner"
    
    # User parameters (0-100 scale)
    discipline: int = 50
    consistency: int = 50
    dedication: int = 50
    focus: int = 50
    
    # Stats
    total_streak_days: int = 0
    total_completions: int = 0
    habits_created: int = 0
    events_joined: int = 0
    events_completed: int = 0
    
    # Collections
    achievements: List[str] = field(default_factory=list)
    joined_events: List[str] = field(default_factory=list)
    completed_events: List[str] = field(default_factory=list)
    
    # Metadata
    created_at: str = field(default_factory=lambda: date.today().isoformat())
    last_active: str = field(default_factory=lambda: date.today().isoformat())
    
    @property
    def xp_to_next_level(self) -> int:
        """Calculate XP needed for next level."""
        return self.level * XP_PER_LEVEL
    
    @property
    def xp_progress(self) -> float:
        """Calculate progress to next level (0.0 to 1.0)."""
        return self.xp / self.xp_to_next_level if self.xp_to_next_level > 0 else 0.0
    
    def add_xp(self, amount: int) -> int:
        """
        Add XP and handle level ups.
        
        Returns:
            Number of levels gained (0 if no level up)
        """
        self.xp += amount
        levels_gained = 0
        
        # Check for level ups
        while self.xp >= self.level * XP_PER_LEVEL:
            self.xp -= self.level * XP_PER_LEVEL
            self.level += 1
            levels_gained += 1
        
        # Update title based on level
        self.title = get_user_title(self.level)
        
        return levels_gained
    
    def get_rank_info(self) -> dict:
        """Get user's global rank badge info."""
        if self.level >= 50:
            return {
                "label": "Legend",
                "color": "#F5A623",
                "icon": "👑",
                "description": "A true habit master"
            }
        elif self.level >= 30:
            return {
                "label": "Diamond",
                "color": "#B9F2FF",
                "icon": "💎",
                "description": "Rare dedication"
            }
        elif self.level >= 20:
            return {
                "label": "Gold",
                "color": "#FFD700",
                "icon": "🥇",
                "description": "Elite habit builder"
            }
        elif self.level >= 15:
            return {
                "label": "Platinum",
                "color": "#E5E4E2",
                "icon": "🏆",
                "description": "Rising champion"
            }
        elif self.level >= 10:
            return {
                "label": "Silver",
                "color": "#C0C0C0",
                "icon": "🥈",
                "description": "Consistent performer"
            }
        elif self.level >= 5:
            return {
                "label": "Bronze",
                "color": "#CD7F32",
                "icon": "🥉",
                "description": "Building momentum"
            }
        elif self.level >= 2:
            return {
                "label": "Intermediate",
                "color": "#4ECDC4",
                "icon": "⭐",
                "description": "On the path"
            }
        else:
            return {
                "label": "Beginner",
                "color": "#94A3B8",
                "icon": "🌱",
                "description": "Just starting out"
            }
    
    def update_parameters(self, habits: list = None):
        """
        Recalculate user parameters based on behavior.
        
        Parameters reflect different aspects of habit building:
        - Discipline: Consistency in completing habits
        - Consistency: How regular the user is
        - Dedication: Time spent and effort
        - Focus: Number of active habits and completion rate
        """
        if habits:
            # Calculate based on habit performance
            total_habits = len(habits)
            completed_today = sum(1 for h in habits if h.is_completed_today())
            
            if total_habits > 0:
                # Discipline: based on today's completion rate
                today_rate = completed_today / total_habits
                self.discipline = min(100, max(1, 
                    int(self.discipline * 0.9 + today_rate * 100 * 0.1)))
                
                # Consistency: based on streaks
                avg_streak = sum(h.get_current_streak() for h in habits) / total_habits
                target_streak = 7  # Aim for week-long streaks
                consistency_score = min(1.0, avg_streak / target_streak)
                self.consistency = min(100, max(1,
                    int(self.consistency * 0.95 + consistency_score * 100 * 0.05)))
                
                # Dedication: based on total completions
                total_completions = sum(h.get_total_completions() for h in habits)
                dedication_score = min(1.0, total_completions / (total_habits * 30))
                self.dedication = min(100, max(1,
                    int(self.dedication * 0.95 + dedication_score * 100 * 0.05)))
                
                # Focus: based on completion rate over 30 days
                avg_rate = sum(h.get_completion_rate(30) for h in habits) / total_habits
                self.focus = min(100, max(1,
                    int(self.focus * 0.95 + avg_rate * 0.05)))
    
    def to_dict(self) -> dict:
        """Convert User to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, d: dict) -> "User":
        """Create User from dictionary."""
        return cls(
            username=d.get("username", "Anonymous"),
            password_hash=d.get("password_hash", ""),
            level=d.get("level", 1),
            xp=d.get("xp", 0),
            title=d.get("title", "Beginner"),
            discipline=d.get("discipline", 50),
            consistency=d.get("consistency", 50),
            dedication=d.get("dedication", 50),
            focus=d.get("focus", 50),
            total_streak_days=d.get("total_streak_days", 0),
            total_completions=d.get("total_completions", 0),
            habits_created=d.get("habits_created", 0),
            events_joined=d.get("events_joined", 0),
            events_completed=d.get("events_completed", 0),
            achievements=d.get("achievements", []),
            joined_events=d.get("joined_events", []),
            completed_events=d.get("completed_events", []),
            created_at=d.get("created_at", date.today().isoformat()),
            last_active=d.get("last_active", date.today().isoformat()),
        )


# ═══════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def hash_password(password: str) -> str:
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def get_user_title(level: int) -> str:
    """Get the title for a given level."""
    titles = {
        1: "Novice",
        2: "Apprentice",
        3: "Learner",
        5: "Explorer",
        10: "Adventurer",
        15: "Challenger",
        20: "Warrior",
        25: "Guardian",
        30: "Champion",
        40: "Master",
        50: "Grand Master",
    }
    
    # Find the highest title the user qualifies for
    qualified_title = "Novice"
    for lvl, title in sorted(titles.items()):
        if level >= lvl:
            qualified_title = title
        else:
            break
    
    return qualified_title


# ═══════════════════════════════════════════════════════════════════════════
# EVENT/CHALLENGE DATA MODEL
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class Event:
    """
    Represents a community challenge/event.
    
    Events are time-bound challenges that users can join
    to work on specific habits together.
    """
    id: str
    name: str
    description: str
    habit_suggestion: str  # e.g., "10 pushups daily"
    emoji: str
    start_date: str
    end_date: str
    xp_reward: int = 100
    participant_count: int = 0
    is_active: bool = True
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, d: dict) -> "Event":
        return cls(**d)


# ═══════════════════════════════════════════════════════════════════════════
# STORAGE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def _ensure_data_dir():
    """Ensure the data directory exists."""
    os.makedirs("data", exist_ok=True)


def load_users() -> List[User]:
    """Load all users from the JSON file."""
    _ensure_data_dir()
    
    if not os.path.exists(USERS_FILE):
        return []
    
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            return []
        
        return [User.from_dict(u) for u in data]
    
    except (json.JSONDecodeError, IOError):
        return []


def save_users(users: List[User]) -> None:
    """Save all users to the JSON file."""
    _ensure_data_dir()
    
    try:
        temp_file = USERS_FILE + ".tmp"
        
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump([u.to_dict() for u in users], f, indent=2, ensure_ascii=False)
        
        os.replace(temp_file, USERS_FILE)
    
    except IOError as e:
        print(f"Error saving users: {e}")
        if os.path.exists(temp_file):
            os.remove(temp_file)


def load_events() -> List[Event]:
    """Load community events from the JSON file."""
    _ensure_data_dir()
    
    events_file = "data/events.json"
    if not os.path.exists(events_file):
        # Create default events
        default_events = create_default_events()
        save_events(default_events)
        return default_events
    
    try:
        with open(events_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            return []
        
        return [Event.from_dict(e) for e in data]
    
    except (json.JSONDecodeError, IOError):
        return create_default_events()


def save_events(events: List[Event]) -> None:
    """Save events to the JSON file."""
    _ensure_data_dir()
    
    events_file = "data/events.json"
    try:
        temp_file = events_file + ".tmp"
        
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump([e.to_dict() for e in events], f, indent=2, ensure_ascii=False)
        
        os.replace(temp_file, events_file)
    
    except IOError as e:
        print(f"Error saving events: {e}")


def create_default_events() -> List[Event]:
    """Create default community events."""
    today = date.today()
    
    return [
        Event(
            id="event_001",
            name="🏋️ 10 Pushups Challenge",
            description="Do 10 pushups every day for 7 days. Build your strength!",
            habit_suggestion="10 Pushups Daily",
            emoji="🏋️",
            start_date=(today - timedelta(days=2)).isoformat(),
            end_date=(today + timedelta(days=5)).isoformat(),
            xp_reward=100,
            is_active=True
        ),
        Event(
            id="event_002",
            name="📚 Read 10 Pages Daily",
            description="Read at least 10 pages of any book every day for 14 days.",
            habit_suggestion="Read 10 Pages",
            emoji="📚",
            start_date=(today - timedelta(days=1)).isoformat(),
            end_date=(today + timedelta(days=13)).isoformat(),
            xp_reward=200,
            is_active=True
        ),
        Event(
            id="event_003",
            name="💧 Hydration Challenge",
            description="Drink 8 glasses of water daily for 10 days.",
            habit_suggestion="8 Glasses of Water",
            emoji="💧",
            start_date=today.isoformat(),
            end_date=(today + timedelta(days=10)).isoformat(),
            xp_reward=150,
            is_active=True
        ),
        Event(
            id="event_004",
            name="🧘 Morning Meditation",
            description="Meditate for 10 minutes every morning for 21 days.",
            habit_suggestion="10 Min Morning Meditation",
            emoji="🧘",
            start_date=(today - timedelta(days=5)).isoformat(),
            end_date=(today + timedelta(days=16)).isoformat(),
            xp_reward=300,
            is_active=True
        ),
    ]


# ═══════════════════════════════════════════════════════════════════════════
# AUTHENTICATION FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def register_user(username: str, password: str) -> tuple:
    """
    Register a new user.
    
    Args:
        username: Desired username
        password: User's password
    
    Returns:
        Tuple of (User object, error message)
        - On success: (User, None)
        - On failure: (None, "error message")
    """
    if not username or not username.strip():
        return None, "Username cannot be empty."
    
    if len(password) < 4:
        return None, "Password must be at least 4 characters."
    
    username = username.strip()
    
    # Check if user already exists
    users = load_users()
    if any(u.username.lower() == username.lower() for u in users):
        return None, "Username already taken."
    
    # Create new user
    password_hash = hash_password(password)
    new_user = User(username=username, password_hash=password_hash)
    
    users.append(new_user)
    save_users(users)
    
    return new_user, None


def login_user(username: str, password: str) -> tuple:
    """
    Authenticate a user.
    
    Args:
        username: User's username
        password: User's password
    
    Returns:
        Tuple of (User object, error message)
        - On success: (User, None)
        - On failure: (None, "error message")
    """
    users = load_users()
    password_hash = hash_password(password)
    
    for user in users:
        if user.username.lower() == username.lower() and user.password_hash == password_hash:
            # Update last active
            user.last_active = date.today().isoformat()
            save_users(users)
            return user, None
    
    return None, "Invalid username or password."


def get_user_by_username(username: str) -> Optional[User]:
    """Get a user by username."""
    users = load_users()
    for user in users:
        if user.username.lower() == username.lower():
            return user
    return None


def update_user(user: User) -> None:
    """Update a user's data in storage."""
    users = load_users()
    for i, u in enumerate(users):
        if u.username == user.username:
            users[i] = user
            break
    save_users(users)


def get_global_rankings(limit: int = 10) -> List[tuple]:
    """
    Get global rankings sorted by level (descending).
    
    Args:
        limit: Number of top users to return
    
    Returns:
        List of tuples (rank, user)
    """
    users = load_users()
    # Sort by level (descending), then by xp (descending)
    users.sort(key=lambda u: (u.level, u.xp), reverse=True)
    
    return [(i + 1, user) for i, user in enumerate(users[:limit])]


def get_user_rank_position(username: str) -> int:
    """Get a user's position in global rankings."""
    users = load_users()
    target_user = None
    
    for user in users:
        if user.username.lower() == username.lower():
            target_user = user
            break
    
    if not target_user:
        return -1
    
    # Sort and find position
    users.sort(key=lambda u: (u.level, u.xp), reverse=True)
    
    for i, user in enumerate(users):
        if user.username == target_user.username:
            return i + 1
    
    return -1


# ═══════════════════════════════════════════════════════════════════════════
# ACHIEVEMENT SYSTEM
# ═══════════════════════════════════════════════════════════════════════════

ACHIEVEMENTS = {
    "first_habit": {
        "name": "First Step",
        "description": "Create your first habit",
        "icon": "🌟",
        "xp_reward": 25
    },
    "streak_3": {
        "name": "Getting Started",
        "description": "Achieve a 3-day streak",
        "icon": "🔥",
        "xp_reward": 50
    },
    "streak_7": {
        "name": "Week Warrior",
        "description": "Achieve a 7-day streak",
        "icon": "⚡",
        "xp_reward": 100
    },
    "streak_14": {
        "name": "Fortnight Fighter",
        "description": "Achieve a 14-day streak",
        "icon": "💪",
        "xp_reward": 200
    },
    "streak_30": {
        "name": "Monthly Master",
        "description": "Achieve a 30-day streak",
        "icon": "🏆",
        "xp_reward": 500
    },
    "level_5": {
        "name": "Rising Star",
        "description": "Reach level 5",
        "icon": "⭐",
        "xp_reward": 100
    },
    "level_10": {
        "name": "Dedicated Builder",
        "description": "Reach level 10",
        "icon": "🌟",
        "xp_reward": 250
    },
    "event_first": {
        "name": "Social Butterfly",
        "description": "Join your first event",
        "icon": "🦋",
        "xp_reward": 50
    },
    "event_complete": {
        "name": "Champion",
        "description": "Complete an event",
        "icon": "🥇",
        "xp_reward": 200
    },
    "habits_5": {
        "name": "Habit Collector",
        "description": "Create 5 habits",
        "icon": "📋",
        "xp_reward": 100
    },
}


def check_achievements(user: User, habits: list = None) -> List[str]:
    """
    Check if user has earned any new achievements.
    
    Returns:
        List of newly earned achievement IDs
    """
    new_achievements = []
    
    # First habit
    if "first_habit" not in user.achievements and habits and len(habits) >= 1:
        new_achievements.append("first_habit")
    
    # Habit collector
    if "habits_5" not in user.achievements and habits and len(habits) >= 5:
        new_achievements.append("habits_5")
    
    # Streak achievements
    if habits:
        best_streak = max((h.get_current_streak() for h in habits), default=0)
        
        streak_achievements = [
            ("streak_3", 3),
            ("streak_7", 7),
            ("streak_14", 14),
            ("streak_30", 30),
        ]
        
        for ach_id, required_streak in streak_achievements:
            if ach_id not in user.achievements and best_streak >= required_streak:
                new_achievements.append(ach_id)
    
    # Level achievements
    level_achievements = [
        ("level_5", 5),
        ("level_10", 10),
    ]
    
    for ach_id, required_level in level_achievements:
        if ach_id not in user.achievements and user.level >= required_level:
            new_achievements.append(ach_id)
    
    # Event achievements
    if "event_first" not in user.achievements and len(user.joined_events) >= 1:
        new_achievements.append("event_first")
    
    if "event_complete" not in user.achievements and len(user.completed_events) >= 1:
        new_achievements.append("event_complete")
    
    # Award XP for new achievements
    for ach_id in new_achievements:
        user.achievements.append(ach_id)
        if ach_id in ACHIEVEMENTS:
            user.add_xp(ACHIEVEMENTS[ach_id]["xp_reward"])
    
    return new_achievements