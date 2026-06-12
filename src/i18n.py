"""
=============================================================================
I18N MODULE - Lightweight translation helper for Streamlit
=============================================================================
This module loads JSON locale files and exposes a `t()` helper.
It stores the active language in Streamlit session state so the choice
survives reruns while the user is in the same session.
=============================================================================
"""

import json
import os
from typing import Dict

import streamlit as st

LOCALES_DIR = os.path.join(os.path.dirname(__file__), "..", "locales")

DEFAULT_LANGUAGE = "en"
SUPPORTED_LANGUAGES = ["en", "hi"]

LANGUAGE_OPTIONS = {
    "en": "English",
    "hi": "हिंदी",
    "te": "తెలుగు",
}


def _load_locale(language: str) -> Dict[str, str]:
    path = os.path.join(LOCALES_DIR, f"{language}.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}


@st.cache_resource(show_spinner=False)
def get_translations(language: str) -> Dict[str, str]:
    en = _load_locale(DEFAULT_LANGUAGE)
    if language == DEFAULT_LANGUAGE:
        return en
    translation = _load_locale(language)
    merged = dict(en)
    merged.update(translation)
    return merged


def get_active_language() -> str:
    return st.session_state.get("app_language", DEFAULT_LANGUAGE)


def set_active_language(language: str) -> None:
    if language not in SUPPORTED_LANGUAGES:
        language = DEFAULT_LANGUAGE
    st.session_state.app_language = language


def t(key: str, **kwargs) -> str:
    language = get_active_language()
    catalog = get_translations(language)
    text = catalog.get(key) or _load_locale(DEFAULT_LANGUAGE).get(key, key)
    if kwargs and isinstance(text, str):
        try:
            text = text.format(**kwargs)
        except Exception:
            pass
    return text


def render_language_selector() -> None:
    current = get_active_language()
    selected = st.selectbox(
        "Language",
        [LANGUAGE_OPTIONS[code] for code in SUPPORTED_LANGUAGES],
        index=SUPPORTED_LANGUAGES.index(current),
        key="language_selector",
    )
    for code, label in LANGUAGE_OPTIONS.items():
        if label == selected:
            set_active_language(code)
            break
