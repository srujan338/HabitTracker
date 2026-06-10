from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Optional


@dataclass
class Habit:
    name: str
    habit_type: str          # "adopt" or "quit"
    emoji: str
    completions: List[str] = field(default_factory=list)   # list of ISO date strings
    created_at: str = field(default_factory=lambda: date.today().isoformat())

    # ── derived stats ──────────────────────────────────────────────

    def is_completed_today(self) -> bool:
        return date.today().isoformat() in self.completions

    def get_current_streak(self) -> int:
        if not self.completions:
            return 0
        sorted_dates = sorted(self.completions, reverse=True)
        streak = 0
        check = date.today()
        for d in sorted_dates:
            if d == check.isoformat():
                streak += 1
                check -= timedelta(days=1)
            elif d == (check + timedelta(days=1)).isoformat():
                # allow today not yet checked
                continue
            else:
                break
        return streak

    def get_longest_streak(self) -> int:
        if not self.completions:
            return 0
        valid_dates = []
        for d in set(self.completions):
            try:
                valid_dates.append(date.fromisoformat(d))
            except (ValueError, TypeError):
                continue
        if not valid_dates:
            return 0
            
        sorted_dates = sorted(valid_dates)
        longest = current = 1
        for i in range(1, len(sorted_dates)):
            a = sorted_dates[i - 1]
            b = sorted_dates[i]
            if (b - a).days == 1:
                current += 1
                longest = max(longest, current)
            else:
                current = 1
        return longest

    def get_total_completions(self) -> int:
        return len(self.completions)

    def get_completion_rate(self, days: int = 30) -> float:
        end = date.today()
        start = end - timedelta(days=days - 1)
        
        valid_completions = []
        for d in self.completions:
            try:
                valid_completions.append(date.fromisoformat(d))
            except (ValueError, TypeError):
                continue
                
        completed = sum(1 for d in valid_completions if start <= d <= end)
        
        try:
            created = date.fromisoformat(self.created_at)
        except (ValueError, TypeError):
            created = date.today()
            
        actual_days = min(days, (end - created).days + 1)
        return round(completed / actual_days * 100, 1) if actual_days > 0 else 0.0

    def get_rank(self) -> dict:
        streak = self.get_current_streak()
        if streak >= 30:
            return {"label": "Legend", "color": "#F5A623", "bg": "rgba(245,166,35,0.12)", "icon": "🏅"}
        elif streak >= 14:
            return {"label": "Gold", "color": "#FFD700", "bg": "rgba(255,215,0,0.12)", "icon": "🥇"}
        elif streak >= 7:
            return {"label": "Silver", "color": "#A8B8C8", "bg": "rgba(168,184,200,0.15)", "icon": "🥈"}
        elif streak >= 3:
            return {"label": "Bronze", "color": "#CD7F32", "bg": "rgba(205,127,50,0.15)", "icon": "🥉"}
        elif streak >= 1:
            return {"label": "Starter", "color": "#4ECDC4", "bg": "rgba(78,205,196,0.12)", "icon": "🌱"}
        else:
            return {"label": "Not started", "color": "#94A3B8", "bg": "rgba(148,163,184,0.08)", "icon": "—"}

    def get_calendar_month(self, year: int, month: int) -> dict:
        """Returns a dict of day→True for completed days in that month."""
        result = {}
        for d in self.completions:
            try:
                dd = date.fromisoformat(d)
                if dd.year == year and dd.month == month:
                    result[dd.day] = True
            except (ValueError, TypeError):
                continue
        return result

    def mark_complete(self) -> bool:
        today = date.today().isoformat()
        if today not in self.completions:
            self.completions.append(today)
            return True
        return False

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "habit_type": self.habit_type,
            "emoji": self.emoji,
            "completions": self.completions,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Habit":
        # Validate completions are strings before passing to constructor
        raw_completions = d.get("completions", [])
        valid_completions = [c for c in raw_completions if isinstance(c, str)]
        
        return cls(
            name=d["name"],
            habit_type=d.get("habit_type", "adopt"),
            emoji=d.get("emoji", "✅"),
            completions=valid_completions,
            created_at=d.get("created_at", date.today().isoformat()),
        )


def add_habit(habits: List[Habit], name: str, habit_type: str, emoji: str) -> tuple:
    if any(h.name.lower() == name.lower() for h in habits):
        return None, "A habit with that name already exists."
    habit = Habit(name=name, habit_type=habit_type, emoji=emoji)
    habits.append(habit)
    return habit, None


def delete_habit(habits: List[Habit], name: str) -> bool:
    for i, h in enumerate(habits):
        if h.name == name:
            habits.pop(i)
            return True
    return False
