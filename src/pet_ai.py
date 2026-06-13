from __future__ import annotations

import datetime
import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class PetMemory:
    user_name: str = ""
    goals: List[str] = field(default_factory=list)
    hobbies: List[str] = field(default_factory=list)
    favorite_subjects: List[str] = field(default_factory=list)
    last_checkin_date: Optional[str] = None
    last_chat_date: Optional[str] = None
    last_topics: List[str] = field(default_factory=list)
    facts: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "user_name": self.user_name,
            "goals": self.goals,
            "hobbies": self.hobbies,
            "favorite_subjects": self.favorite_subjects,
            "last_checkin_date": self.last_checkin_date,
            "last_chat_date": self.last_chat_date,
            "last_topics": self.last_topics,
            "facts": self.facts,
        }

    @classmethod
    def from_dict(cls, data: Optional[dict]) -> "PetMemory":
        if not data:
            return cls()
        return cls(
            user_name=data.get("user_name", ""),
            goals=list(data.get("goals", [])),
            hobbies=list(data.get("hobbies", [])),
            favorite_subjects=list(data.get("favorite_subjects", [])),
            last_checkin_date=data.get("last_checkin_date"),
            last_chat_date=data.get("last_chat_date"),
            last_topics=list(data.get("last_topics", [])),
            facts=list(data.get("facts", [])),
        )


@dataclass
class PetState:
    user_id: str
    pet_type: str = "dog"
    personality_type: str = ""
    pet_name: str = "Buddy"
    xp: int = 0
    level: int = 1
    growth_stage: str = "baby_pet"
    conversation_history: List[dict] = field(default_factory=list)
    memory: PetMemory = field(default_factory=PetMemory)
    unlocked_achievements: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "pet_type": self.pet_type,
            "personality_type": self.personality_type,
            "pet_name": self.pet_name,
            "xp": self.xp,
            "level": self.level,
            "growth_stage": self.growth_stage,
            "conversation_history": self.conversation_history[-50:],
            "memory": self.memory.to_dict(),
            "unlocked_achievements": self.unlocked_achievements,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PetState":
        return cls(
            user_id=data.get("user_id", ""),
            pet_type=data.get("pet_type", "dog"),
            personality_type=data.get("personality_type", ""),
            pet_name=data.get("pet_name", "Buddy"),
            xp=int(data.get("xp", 0) or 0),
            level=int(data.get("level", 1) or 1),
            growth_stage=data.get("growth_stage", "baby_pet"),
            conversation_history=list(data.get("conversation_history", [])),
            memory=PetMemory.from_dict(data.get("memory")),
            unlocked_achievements=list(data.get("unlocked_achievements", [])),
        )

    def add_xp(self, amount: int) -> int:
        previous = self.level
        self.xp += amount
        thresholds = [0, 50, 150, 300, 500, 800]
        self.level = max(index + 1 for index, value in enumerate(thresholds) if self.xp >= value)
        if self.level <= 1:
            self.growth_stage = "baby_pet"
        elif self.level <= 2:
            self.growth_stage = "young_pet"
        elif self.level <= 3:
            self.growth_stage = "adult_pet"
        else:
            self.growth_stage = "legendary_pet"
        return self.level - previous


STATE_FILE = "data/pet_states.json"
PET_MAP: Dict[str, dict] = {
    "dragon": {"emoji": "🐉", "label": "Dragon", "tone": "confident and motivational", "challenges": ["Claim one bold win today.", "Do one 10-minute power push.", "Pick one challenge and own it."]},
    "cat": {"emoji": "🐈", "label": "Cat", "tone": "sarcastic but caring", "challenges": ["Try one small creative twist today.", "Do one task with a fresh approach.", "Schedule one playful break after your work block."]},
    "dog": {"emoji": "🐕", "label": "Dog", "tone": "enthusiastic and supportive", "challenges": ["Show up for one tiny simple action today.", "Celebrate even a small attempt.", "Do a short accountability check with yourself."]},
    "owl": {"emoji": "🦉", "label": "Owl", "tone": "wise and thoughtful", "challenges": ["Write one clear intention for the day.", "Break one longer task into smaller steps.", "Review what worked yesterday in one sentence."]},
    "fox": {"emoji": "🦊", "label": "Fox", "tone": "playful and clever", "challenges": ["Turn one habit into a mini experiment.", "Discover one shortcut or improvement today.", "Reframe a boring task as a playful challenge."]},
}


def _load_store() -> dict:
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f) or {}
    except (json.JSONDecodeError, OSError):
        pass
    return {}


def _save_store(store: dict) -> None:
    try:
        os.makedirs(os.path.dirname(STATE_FILE) or ".", exist_ok=True)
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(store, f, indent=2)
    except OSError:
        pass


def load_state(user_id: str) -> PetState:
    store = _load_store()
    data = store.get(user_id)
    if data:
        return PetState.from_dict(data)
    return PetState(user_id=user_id)


def save_state(state: PetState) -> None:
    store = _load_store()
    store[state.user_id] = state.to_dict()
    _save_store(store)


def days_since(value: Optional[str]) -> int:
    if not value:
        return 999
    try:
        return (datetime.datetime.utcnow() - datetime.datetime.fromisoformat(value)).days
    except (TypeError, ValueError):
        return 999


def mood_for_state(state: PetState, last_activity: Optional[str], completed_today: int, total: int) -> str:
    if total <= 0 and (not last_activity or days_since(last_activity) > 1):
        return "worried"
    if completed_today >= total and total > 0:
        return "excited"
    if completed_today > 0 and completed_today < total:
        return "curious"
    if not last_activity:
        return "sleepy"
    if days_since(last_activity) >= 2:
        return "sleepy"
    return "happy"


def daily_challenge(state: PetState) -> str:
    import random
    options = PET_MAP.get(state.pet_type, PET_MAP["dog"]).get("challenges", ["Learn one new thing today."])
    return random.choice(options)


def pet_reply(state: PetState, message: str) -> str:
    try:
        from openai import OpenAI
    except ImportError:
        return _fallback_reply(state, message)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return _fallback_reply(state, message)
    system = _build_system_prompt(state)
    try:
        client = OpenAI(api_key=api_key)
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": system}, {"role": "user", "content": message}],
            temperature=0.7,
            max_tokens=160,
        )
        reply = completion.choices[0].message.content or ""
        return reply.strip() or _fallback_reply(state, message)
    except Exception:
        return _fallback_reply(state, message)


def _build_system_prompt(state: PetState) -> str:
    pet = PET_MAP.get(state.pet_type or "dog", PET_MAP["dog"])
    tone = pet.get("tone", "friendly")
    name = state.pet_name or pet.get("label", "Pet")
    recent = ". ".join((state.memory.last_topics or [])[-3:])
    facts = "; ".join((state.memory.facts or [])[-6:])
    prompt = f"You are {name}, a {pet.get('label', 'pet')} companion with a {tone} tone. Keep replies short for chat UI."
    if facts:
        prompt += f" Known facts: {facts}."
    if recent:
        prompt += f" Recent thread: {recent}."
    return prompt


def _fallback_reply(state: PetState, message: str) -> str:
    picks = {
        "dragon": ["Stay sharp.", "Use this moment.", "Keep discipline strong."],
        "cat": ["Interesting.", "Curious move.", "Make it count."],
        "dog": ["Let's do it!", "You've got this.", "Nice start."],
        "owl": ["Plan the next small step.", "Focus improves results.", "One thoughtful move matters."],
        "fox": ["Turn that into play.", "Try one clever tweak.", "Have fun with it."],
    }
    options = picks.get(state.pet_type, picks["dog"])
    return options[hash(message) % len(options)]


def update_memory_from_message(state: PetState, message: str) -> None:
    lowered = message.lower()
    if not state.memory.user_name and len(message.split()) <= 4:
        state.memory.user_name = message.strip()
    for keyword in ("goal", "target", "learning", "learn", "improve"):
        if keyword in lowered and keyword not in state.memory.goals:
            state.memory.goals.append(keyword)
            break
    for keyword in ("hobby", "fun", "play", "enjoy"):
        if keyword in lowered and keyword not in state.memory.hobbies:
            state.memory.hobbies.append(keyword)
            break
    for keyword in ("subject", "topic", "computer", "math", "english"):
        if keyword in lowered and keyword not in state.memory.favorite_subjects:
            state.memory.favorite_subjects.append(keyword)
            break
    state.memory.last_topics.append(message)
    if len(state.memory.last_topics) > 20:
        state.memory.last_topics = state.memory.last_topics[-20:]
    state.memory.facts.append(message)
    if len(state.memory.facts) > 20:
        state.memory.facts = state.memory.facts[-20:]
    state.memory.last_chat_date = datetime.date.today().isoformat()
