"""
Companion-style screen pet module.

The companion is a small animated pet that lives in the bottom corners
of the virtual screen, reacts to user actions, and switches between
idle, happy, excited, and sleepy moods.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass(frozen=True)
class PetType:
    code: str
    emoji: str
    label: str
    color: str
    personality: str
    greeting: str
    keywords: tuple[str, ...]


PET_TYPES: Dict[str, PetType] = {
    "dragon": PetType(
        code="dragon",
        emoji="🐉",
        label="Dragon",
        color="#ef4444",
        personality="bold",
        greeting="Keep your fire lit",
        keywords=("bold", "leader", "determined", "risk", "challenge"),
    ),
    "cat": PetType(
        code="cat",
        emoji="🐱",
        label="Cat",
        color="#a855f7",
        personality="sarcastic",
        greeting="Make it interesting",
        keywords=("creative", "curious", "unique", "quiet", "style"),
    ),
    "dog": PetType(
        code="dog",
        emoji="🐶",
        label="Dog",
        color="#facc15",
        personality="loyal",
        greeting="Let's go together",
        keywords=("loyal", "friendly", "routine", "team", "support"),
    ),
    "owl": PetType(
        code="owl",
        emoji="🦉",
        label="Owl",
        color="#38bdf8",
        personality="wise",
        greeting="One clear focus",
        keywords=("learner", "study", "calm", "focus", "thoughtful"),
    ),
    "fox": PetType(
        code="fox",
        emoji="🦊",
        label="Fox",
        color="#fb923c",
        personality="clever",
        greeting="Try a new trick today",
        keywords=("clever", "playful", "adaptive", "new", "fun"),
    ),
}


def pet_type_for_code(code: str) -> PetType:
    return PET_TYPES.get(code, next(iter(PET_TYPES.values())))


def assign_pet_type_from_answers(answers: Optional[dict] = None) -> str:
    answers = answers or {}
    personality = str(answers.get("motivation_style") or answers.get("identity") or "").lower()
    mood = str(answers.get("energy") or "").lower()
    text = " ".join(str(v).lower() for v in answers.values() if isinstance(v, str))

    if any(word in text for word in ["leader", "bold", "challenge", "risk", "target", "direct"]):
        return "dragon"
    if any(word in text for word in ["creative", "curious", "unique", "quiet", "style", "sarcastic"]):
        return "cat"
    if any(word in text for word in ["loyal", "friendly", "routine", "team", "support", "accountability"]):
        return "dog"
    if any(word in text for word in ["learner", "study", "calm", "focus", "thoughtful", "quiet"]):
        return "owl"
    return "fox"
