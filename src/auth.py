"""
=============================================================================
AUTH MODULE - Supabase Authentication & Profile Management
=============================================================================
This module handles user management using Supabase (PostgreSQL).
=============================================================================
"""

import hashlib
import os
import re
from datetime import date
from typing import List, Optional
from dataclasses import dataclass, field, asdict
from src.supabase_client import supabase

# Configuration
XP_PER_LEVEL = 100
USERS_TABLE = "users"
ACHIEVEMENTS = {
    "first_habit": {"name": "First Step", "description": "Create your first habit", "icon": "🌟", "xp_reward": 25},
    "streak_3": {"name": "Getting Started", "description": "Achieve a 3-day streak", "icon": "🔥", "xp_reward": 50},
    "streak_7": {"name": "Week Strong", "description": "Achieve a 7-day streak", "icon": "⚡", "xp_reward": 100},
    "habits_5": {"name": "Habit Collector", "description": "Create 5 habits", "icon": "📋", "xp_reward": 100},
}
XP_HABIT_COMPLETION = 10
XP_STREAK_BONUS = 5

@dataclass
class User:
    """Represents a user with gamification features."""
    username: str
    password_hash: str = ""
    google_id: Optional[str] = None
    email: Optional[str] = None
    level: int = 1
    xp: int = 0
    title: str = "Beginner"
    discipline: int = 50
    consistency: int = 50
    dedication: int = 50
    focus: int = 50
    creativity: int = 50
    resilience: int = 50
    total_streak_days: int = 0
    total_completions: int = 0
    habits_created: int = 0
    events_joined: int = 0
    events_completed: int = 0
    onboarding_completed: bool = False
    personality_type: str = "Balanced Builder"
    preferred_tone: str = "Friendly and direct"
    pet_name: str = "Buddy"
    pet_mood: str = "curious"
    achievements: List[str] = field(default_factory=list)
    joined_events: List[str] = field(default_factory=list)
    completed_events: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: date.today().isoformat())
    last_active: str = field(default_factory=lambda: date.today().isoformat())
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, d: dict) -> "User":
        data = {k: v for k, v in d.items() if k in cls.__annotations__}
        return cls(**data)
    
    @property
    def xp_to_next_level(self) -> int:
        return self.level * XP_PER_LEVEL
    
    @property
    def xp_progress(self) -> float:
        return self.xp / self.xp_to_next_level if self.xp_to_next_level > 0 else 0.0
    
    def add_xp(self, amount: int) -> int:
        self.xp += amount
        levels_gained = 0
        while self.xp >= self.level * XP_PER_LEVEL:
            self.xp -= self.level * XP_PER_LEVEL
            self.level += 1
            levels_gained += 1
        self.title = get_user_title(self.level)
        return levels_gained

    def update_parameters(self, habits: list = None):
        """Recalculate trait stats from current habit behavior."""
        if not habits:
            return

        total_habits = len(habits)
        if total_habits == 0:
            return

        completed_today = sum(1 for h in habits if h.is_completed_today())
        today_rate = completed_today / total_habits
        avg_streak = sum(h.get_current_streak() for h in habits) / total_habits
        total_done = sum(h.get_total_completions() for h in habits)
        avg_rate = sum(h.get_completion_rate(30) for h in habits) / total_habits
        quit_habits = sum(1 for h in habits if h.habit_type == "quit")

        # Calculate performance score for each category
        categories_habits = {
            "health": [h for h in habits if getattr(h, "category", None) == "health"],
            "lifestyle": [h for h in habits if getattr(h, "category", None) == "lifestyle"],
            "finance": [h for h in habits if getattr(h, "category", None) == "finance"],
            "learning": [h for h in habits if getattr(h, "category", None) == "learning"],
            "productivity": [h for h in habits if getattr(h, "category", None) == "productivity"],
            "mindfulness": [h for h in habits if getattr(h, "category", None) == "mindfulness"],
            "creativity": [h for h in habits if getattr(h, "category", None) == "creativity"],
        }

        scores = {}
        for cat, cat_habits in categories_habits.items():
            if not cat_habits:
                continue
            cat_today = sum(1 for h in cat_habits if h.is_completed_today()) / len(cat_habits)
            cat_avg_rate = sum(h.get_completion_rate(30) for h in cat_habits) / len(cat_habits)
            cat_avg_streak = sum(h.get_current_streak() for h in cat_habits) / len(cat_habits)
            scores[cat] = (cat_today * 40) + (cat_avg_rate * 0.4) + (min(cat_avg_streak / 7, 1) * 20)

        # Update discipline: productivity and health
        discipline_sources = [scores[c] for c in ["productivity", "health"] if c in scores]
        if discipline_sources:
            target_discipline = sum(discipline_sources) / len(discipline_sources)
            self.discipline = _blend_score(self.discipline, target_discipline, 0.12)
        else:
            self.discipline = _blend_score(self.discipline, today_rate * 100, 0.12)

        # Update consistency: lifestyle and mindfulness
        consistency_sources = [scores[c] for c in ["lifestyle", "mindfulness"] if c in scores]
        if consistency_sources:
            target_consistency = sum(consistency_sources) / len(consistency_sources)
            self.consistency = _blend_score(self.consistency, target_consistency, 0.08)
        else:
            self.consistency = _blend_score(self.consistency, min(avg_streak / 7, 1) * 100, 0.08)

        # Update dedication: finance and creativity
        dedication_sources = [scores[c] for c in ["finance", "creativity"] if c in scores]
        if dedication_sources:
            target_dedication = sum(dedication_sources) / len(dedication_sources)
            self.dedication = _blend_score(self.dedication, target_dedication, 0.08)
        else:
            self.dedication = _blend_score(self.dedication, min(total_done / (total_habits * 30), 1) * 100, 0.08)

        # Update focus: learning and productivity
        focus_sources = [scores[c] for c in ["learning", "productivity"] if c in scores]
        if focus_sources:
            target_focus = sum(focus_sources) / len(focus_sources)
            self.focus = _blend_score(self.focus, target_focus, 0.08)
        else:
            self.focus = _blend_score(self.focus, avg_rate, 0.08)

        # Update creativity: creativity and learning
        creativity_sources = [scores[c] for c in ["creativity", "learning"] if c in scores]
        if creativity_sources:
            target_creativity = sum(creativity_sources) / len(creativity_sources)
            self.creativity = _blend_score(self.creativity, target_creativity, 0.04)
        else:
            self.creativity = _blend_score(self.creativity, min(total_habits / 6, 1) * 100, 0.04)

        # Update resilience: health, mindfulness, lifestyle
        resilience_sources = [scores[c] for c in ["health", "mindfulness", "lifestyle"] if c in scores]
        if resilience_sources:
            target_resilience = sum(resilience_sources) / len(resilience_sources)
            if quit_habits > 0:
                target_resilience = min(100, target_resilience + 10)
            self.resilience = _blend_score(self.resilience, target_resilience, 0.06)
        else:
            self.resilience = _blend_score(self.resilience, min((avg_streak + quit_habits) / 8, 1) * 100, 0.06)

        self.total_streak_days = int(sum(h.get_current_streak() for h in habits))
    
    def get_rank_info(self) -> dict:
        if self.level >= 50: return {"label": "Legend", "color": "#F5A623", "icon": "👑"}
        elif self.level >= 30: return {"label": "Diamond", "color": "#B9F2FF", "icon": "💎"}
        elif self.level >= 20: return {"label": "Gold", "color": "#FFD700", "icon": "🥇"}
        elif self.level >= 15: return {"label": "Platinum", "color": "#E5E4E2", "icon": "🏆"}
        elif self.level >= 10: return {"label": "Silver", "color": "#C0C0C0", "icon": "🥈"}
        elif self.level >= 5: return {"label": "Bronze", "color": "#CD7F32", "icon": "🥉"}
        elif self.level >= 2: return {"label": "Intermediate", "color": "#4ECDC4", "icon": "⭐"}
        else: return {"label": "Beginner", "color": "#94A3B8", "icon": "🌱"}

@dataclass
class Event:
    id: str
    name: str
    description: str
    habit_suggestion: str
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
        return cls(**{k: v for k, v in d.items() if k in cls.__annotations__})

# Authentication & Storage
def register_user(username: str, password: str) -> tuple:
    if not username or not username.strip(): return None, "Username cannot be empty."
    if len(password) < 4: return None, "Password must be at least 4 characters."
    
    normalized_username = username.strip().lower()
    response = supabase.table(USERS_TABLE).select("*").eq("username", normalized_username).execute()
    if response.data: return None, "Username already taken."
        
    new_user = User(username=normalized_username, password_hash=hashlib.sha256(password.encode()).hexdigest())
    _write_user_payload("insert", new_user.to_dict())
    return new_user, None

def login_user(username: str, password: str) -> tuple:
    response = supabase.table(USERS_TABLE).select("*").eq("username", username.lower()).eq("password_hash", hashlib.sha256(password.encode()).hexdigest()).execute()
    
    if response.data:
        return User.from_dict(response.data[0]), None
    return None, "Invalid username or password."

def update_user(user: User) -> None:
    user_dict = user.to_dict()
    if "_id" in user_dict: del user_dict["_id"]
    _write_user_payload("update", user_dict, user.username)

def load_users() -> List[User]:
    response = supabase.table(USERS_TABLE).select("*").execute()
    return [User.from_dict(u) for u in response.data]

def get_user_by_username(username: str) -> Optional[User]:
    response = supabase.table(USERS_TABLE).select("*").eq("username", username.lower()).execute()
    if response.data:
        return User.from_dict(response.data[0])
    return None

def get_google_oauth_url() -> tuple:
    """Create a Supabase Google OAuth URL for Streamlit."""
    redirect_to = os.getenv("SUPABASE_AUTH_REDIRECT_URL", "http://localhost:8501")
    try:
        response = supabase.auth.sign_in_with_oauth({
            "provider": "google",
            "options": {"redirect_to": redirect_to},
        })
        return response.url, None
    except Exception as exc:
        return None, f"Could not start Google login: {exc}"

def login_with_google_code(code: str) -> tuple:
    """Exchange an OAuth callback code and create/load the app profile."""
    try:
        response = supabase.auth.exchange_code_for_session({"auth_code": code})
    except Exception as exc:
        return None, f"Google login failed at exchange step: {exc}"

    auth_user = getattr(response, "user", None)
    if auth_user is None:
        return None, "Google login did not return a user."

    email = getattr(auth_user, "email", None) or ""
    google_id = getattr(auth_user, "id", None) or ""
    if not google_id:
        return None, "Google login returned an account without an id."

    username = _username_from_email(email, google_id)

    existing = get_user_by_google_id(google_id) or get_user_by_username(username)
    if existing:
        existing.google_id = existing.google_id or google_id
        existing.email = existing.email or email
        existing.last_active = date.today().isoformat()
        update_user(existing)
        return existing, None

    new_user = User(
        username=username,
        google_id=google_id,
        email=email,
        password_hash="",
        onboarding_completed=False,
    )
    _write_user_payload("insert", new_user.to_dict())
    return new_user, None

def get_user_by_google_id(google_id: str) -> Optional[User]:
    response = supabase.table(USERS_TABLE).select("*").eq("google_id", google_id).execute()
    if response.data:
        return User.from_dict(response.data[0])
    return None

def _write_user_payload(operation: str, payload: dict, username: str = None) -> None:
    """Write users while tolerating a partially migrated Supabase schema."""
    working_payload = dict(payload)
    missing_columns = set()

    for _ in range(20):
        try:
            if operation == "insert":
                supabase.table(USERS_TABLE).insert(working_payload).execute()
            elif operation == "update":
                supabase.table(USERS_TABLE).update(working_payload).eq("username", username).execute()
            else:
                raise ValueError(f"Unknown user write operation: {operation}")
            return
        except Exception as exc:
            column = _extract_missing_column(str(exc))
            if not column or column in missing_columns or column not in working_payload:
                raise
            missing_columns.add(column)
            del working_payload[column]

def _extract_missing_column(error_text: str) -> Optional[str]:
    match = re.search(r"Could not find the '([^']+)' column", error_text)
    if match:
        return match.group(1)
    return None

def get_global_rankings(limit: int = 10) -> List[tuple]:
    response = supabase.table(USERS_TABLE).select("*").order("level", desc=True).order("xp", desc=True).limit(limit).execute()
    users = [User.from_dict(u) for u in response.data]
    return [(i + 1, user) for i, user in enumerate(users)]

def get_user_rank_position(username: str) -> int:
    users = load_users()
    users.sort(key=lambda u: (u.level, u.xp), reverse=True)
    for i, user in enumerate(users):
        if user.username.lower() == username.lower():
            return i + 1
    return -1

def check_achievements(user: User, habits: list = None) -> List[str]:
    new_achievements = []
    if habits and "first_habit" not in user.achievements and len(habits) >= 1:
        new_achievements.append("first_habit")
    if habits and "habits_5" not in user.achievements and len(habits) >= 5:
        new_achievements.append("habits_5")
    if habits:
        best_streak = max((h.get_current_streak() for h in habits), default=0)
        for ach_id, required in [("streak_3", 3), ("streak_7", 7)]:
            if ach_id not in user.achievements and best_streak >= required:
                new_achievements.append(ach_id)

    for ach_id in new_achievements:
        user.achievements.append(ach_id)
        user.add_xp(ACHIEVEMENTS[ach_id]["xp_reward"])
    return new_achievements

# Event Functions
def load_events() -> List[Event]:
    return []

def save_events(events: List[Event]) -> None:
    pass

def apply_onboarding_profile(user: User, answers: dict) -> None:
    """Convert quiz answers into initial user traits and companion style."""
    scores = {
        "discipline": 45,
        "consistency": 45,
        "dedication": 45,
        "focus": 45,
        "creativity": 45,
        "resilience": 45,
    }

    for values in answers.values():
        if not isinstance(values, list):
            values = [values]
        for value in values:
            for trait, delta in QUIZ_SCORE_MAP.get(value, {}).items():
                scores[trait] = min(95, max(15, scores[trait] + delta))

    for trait, score in scores.items():
        setattr(user, trait, score)

    top_trait = max(scores, key=scores.get)
    user.personality_type = {
        "discipline": "Structured Achiever",
        "consistency": "Steady Builder",
        "dedication": "Deep Worker",
        "focus": "Precision Planner",
        "creativity": "Creative Explorer",
        "resilience": "Comeback Specialist",
    }[top_trait]
    user.preferred_tone = answers.get("motivation_style", "Friendly and direct")
    user.pet_name = answers.get("companion_name") or "Buddy"
    user.pet_mood = "energized"
    user.onboarding_completed = True
    user.last_active = date.today().isoformat()

def _blend_score(current: int, target: float, weight: float) -> int:
    return min(100, max(1, int(current * (1 - weight) + target * weight)))

def _username_from_email(email: str, fallback: str) -> str:
    if email and "@" in email:
        return email.split("@", 1)[0].strip().lower()
    return f"google_{fallback[:8]}"

def get_user_title(level: int) -> str:
    titles = {
        1: "Novice",
        2: "Apprentice",
        3: "Learner",
        5: "Explorer",
        10: "Adventurer",
        15: "Challenger",
        20: "Warrior",
        30: "Champion",
        40: "Master",
        50: "Grand Master",
    }
    title = "Novice"
    for required_level, name in sorted(titles.items()):
        if level >= required_level:
            title = name
    return title

QUIZ_SCORE_MAP = {
    "I follow a plan and like checking things off": {"discipline": 16, "focus": 8},
    "I get bursts of energy and enjoy experimenting": {"creativity": 16, "resilience": 6},
    "I am steady when the system is simple": {"consistency": 16, "discipline": 6},
    "I restart well after missing days": {"resilience": 18, "consistency": 5},
    "Clear targets": {"focus": 12, "discipline": 8},
    "Variety and novelty": {"creativity": 14, "dedication": 4},
    "Accountability": {"consistency": 10, "dedication": 8},
    "A calm routine": {"focus": 10, "consistency": 10},
    "Morning": {"discipline": 8, "focus": 6},
    "Afternoon": {"dedication": 8, "creativity": 4},
    "Evening": {"resilience": 8, "consistency": 4},
    "Late night": {"creativity": 8, "resilience": 4},
    "Gentle encouragement": {"resilience": 8},
    "Direct challenge": {"discipline": 8, "dedication": 6},
    "Playful praise": {"creativity": 8, "consistency": 4},
    "Quiet reminders": {"focus": 8, "consistency": 4},
    "Health and energy": {"discipline": 8, "dedication": 8},
    "Learning and skills": {"focus": 8, "creativity": 8},
    "Mindfulness": {"resilience": 8, "focus": 8},
    "Productivity": {"discipline": 8, "focus": 8},
    "Creativity": {"creativity": 14},
    "Social confidence": {"resilience": 8, "dedication": 6},
}
