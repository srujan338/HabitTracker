"""
Companion-style screen pet.

Renders a persistent animated companion in the bottom-right of the app UI.
"""

from __future__ import annotations

from typing import Dict, Optional

import streamlit as st

from src.pet_types import pet_type_for_code
from src.pet_ai import load_state


STATE_KEY = "companion_visible"
SPEAK_KEY = "companion_speak"


def _get_user_id() -> str:
    user = st.session_state.get("current_user")
    if not user:
        return "default"
    return getattr(user, "username", "default")


def _state_for(user_id: str):
    try:
        return load_state(user_id)
    except Exception:
        return None


def _mood_from_pet_state(state):
    try:
        from src.pet_ai import mood_for_state
        today = st.session_state.get("habits", [])
        done = sum(1 for h in today if h.is_completed_today())
        meta = getattr(st.session_state.get("current_user"), "meta", {}) or {}
        last = meta.get("last_activity") or getattr(state, "last_chat_date", None)
        return mood_for_state(state, last, done, len(today))
    except Exception:
        return "happy"


def _reaction_for(state) -> str:
    if not state:
        return "Tap me!"
    pet = pet_type_for_code(state.pet_type)
    mood = _mood_from_pet_state(state)
    reactions = {
        "excited": f"{pet.emoji} Super charged!",
        "happy": f"{pet.emoji} Glad you're here",
        "curious": f"{pet.emoji} What's next?",
        "worried": f"{pet.emoji} Missed you lately",
        "sleepy": f"{pet.emoji} *yawn*",
    }
    base = reactions.get(mood, f"{pet.emoji} Ready")
    last_speak = st.session_state.get(SPEAK_KEY)
    if not last_speak:
        st.session_state[SPEAK_KEY] = base
    return st.session_state.get(SPEAK_KEY, base)


def speak(text: str) -> None:
    st.session_state[SPEAK_KEY] = text


def _pet_style() -> str:
    return """
    <style>
    .screen-pet {
      position: fixed;
      z-index: 10000;
      width: 160px;
      font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial;
      filter: drop-shadow(0 12px 30px rgba(0,0,0,0.4));
      animation: roam 80s linear infinite, float 4s ease-in-out infinite;
      transition: transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
      cursor: pointer;
      pointer-events: auto;
      user-select: none;
    }
    .screen-pet:hover {
      animation-play-state: paused;
      transform: scale(1.15) rotate(2deg);
    }
    .screen-pet-card {
      background: rgba(15, 23, 42, 0.85);
      border: 1px solid rgba(255, 255, 255, 0.15);
      backdrop-filter: blur(20px) saturate(160%);
      border-radius: 24px;
      padding: 12px;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 8px;
    }
    .screen-pet-avatar {
      font-size: 48px;
      line-height: 1;
      filter: drop-shadow(0 0 10px rgba(255,255,255,0.2));
    }
    .screen-pet-bubble {
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid rgba(255, 255, 255, 0.1);
      color: #f8fafc;
      border-radius: 16px;
      padding: 8px 12px;
      font-size: 13px;
      line-height: 1.4;
      text-align: center;
      width: 100%;
    }
    .screen-pet-meta {
      color: rgba(255, 255, 255, 0.5);
      font-size: 10px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }
    .pet-trigger-hidden {
      display: none !important;
    }
    
    @keyframes roam {
      0%   { left: 85%; top: 75%; }
      15%  { left: 15%; top: 80%; }
      30%  { left: 10%; top: 15%; }
      45%  { left: 80%; top: 20%; }
      60%  { left: 45%; top: 50%; }
      75%  { left: 15%; top: 25%; }
      90%  { left: 85%; top: 15%; }
      100% { left: 85%; top: 75%; }
    }
    @keyframes float {
      0%, 100% { transform: translateY(0px); }
      50% { transform: translateY(-12px); }
    }
    </style>
    """


def render_companion() -> None:
    try:
        user_id = _get_user_id()
        state = _state_for(user_id)
        pet = pet_type_for_code(getattr(state, "pet_type", "fox") if state else "fox")
        mood = _mood_from_pet_state(state) if state else "happy"

        if SPEAK_KEY not in st.session_state:
            st.session_state[SPEAK_KEY] = _reaction_for(state)

        st.markdown(_pet_style(), unsafe_allow_html=True)

        # Invisible trigger button for Streamlit logic
        st.markdown('<div class="pet-trigger-hidden">', unsafe_allow_html=True)
        if st.button("talk", key="companion_trigger"):
            st.session_state[SPEAK_KEY] = _reaction_for(state)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        # Visual floating pet
        # We use a script to find the button inside the hidden div and click it
        st.markdown(
            f"""
            <div class="screen-pet" onclick="
                const btns = window.parent.document.querySelectorAll('button');
                for (const btn of btns) {{
                    if (btn.innerText === 'talk') {{
                        btn.click();
                        break;
                    }}
                }}
            ">
              <div class="screen-pet-card">
                <div class="screen-pet-avatar">{pet.emoji}</div>
                <div class="screen-pet-bubble">{st.session_state[SPEAK_KEY]}</div>
                <div class="screen-pet-meta">{mood} • {pet.label}</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    except Exception:
        pass


def ensure_visible() -> None:
    st.session_state[STATE_KEY] = True


def hide() -> None:
    st.session_state[STATE_KEY] = False
