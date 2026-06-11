import json
import os
import streamlit as st

DEFAULT_LANG = "en"
TRANSLATIONS_DIR = "data/translations"

def load_translations(lang):
    file_path = os.path.join(TRANSLATIONS_DIR, f"{lang}.json")
    if not os.path.exists(file_path):
        file_path = os.path.join(TRANSLATIONS_DIR, f"{DEFAULT_LANG}.json")
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def translate(key, **kwargs):
    if "translations" not in st.session_state:
        st.session_state.translations = load_translations(st.session_state.get("language", DEFAULT_LANG))
    
    text = st.session_state.translations.get(key, key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except KeyError:
            return text
    return text

def set_language(lang):
    st.session_state.language = lang
    st.session_state.translations = load_translations(lang)
