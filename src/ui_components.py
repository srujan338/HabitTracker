"""
=============================================================================
MENTORSHIP NOTE: UI COMPONENTS (Building Blocks)
=============================================================================
In professional software engineering, we avoid repeating the same code.
Instead, we build "Components" — like LEGO blocks. 

This file contains functions that draw specific parts of the screen.
When you want to show a card or a badge, you just "call" these functions.
This makes your 'main.py' much smaller and easier to read!
=============================================================================
"""

import streamlit as st
from datetime import date
import calendar

def glass_card_start():
    """Prints the opening HTML for a glassy card."""
    st.markdown('<div class="glass-card main-content">', unsafe_allow_html=True)

def glass_card_end():
    """Prints the closing HTML for a glassy card."""
    st.markdown('</div>', unsafe_allow_html=True)

def section_title(text: str, margin_top: str = "8px"):
    """
    Renders a small, uppercase title used for sections.
    Mentorship Tip: Using 'text-transform: uppercase' in CSS is better than 
    typing in ALL CAPS in Python. It's more flexible!
    """
    st.markdown(
        f'<p style="font-size:11px;font-weight:700;color:var(--text3);text-transform:uppercase;'
        f'letter-spacing:0.1em;margin:{margin_top} 0 16px;">{text}</p>',
        unsafe_allow_html=True,
    )

def rank_badge(rank: dict, text_only: bool = False) -> str:
    """
    Creates the HTML for a rank badge (like 'Legend' or 'Starter').
    
    Args:
        rank: A dictionary with 'label', 'color', 'bg', and 'icon'.
        text_only: If True, returns a simpler version without the background box.
    """
    if text_only:
        return f'<span style="color:{rank["color"]};">{rank["icon"]} {rank["label"]}</span>'
    
    return (
        f'<span style="display:inline-block;background:{rank["bg"]};color:{rank["color"]};'
        f'border-radius:12px;padding:4px 12px;font-size:11px;font-weight:700;letter-spacing:0.05em;border:0.5px solid {rank["color"]}33;">'
        f'{rank["icon"]} {rank["label"]}</span>'
    )

def render_top_nav(habits: list, active_page: str, theme: str):
    """
    The Navigation Bar at the top of the screen.
    
    MENTORSHIP NOTE: We use 'st.columns' to space out the Logo, the Buttons, 
    and the Theme Toggle horizontally.
    """
    # 1. Background Bar (The glassy rectangle)
    st.markdown(
        """
        <div class="nav-bar">
            <div style="display: flex; justify-content: space-between; align-items: center; max-width: 1200px; margin: 0 auto; width: 100%;">
                <h1 style="font-size: 24px; margin: 0; font-family: 'Space Grotesk', sans-serif;">
                    habit<span style="color: var(--accent2);">.</span>space
                </h1>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # 2. Interactive elements (The actual buttons)
    # We use columns to align things with the background bar above.
    cols = st.columns([2.5, 5, 1.5])
    
    with cols[1]:
        pages = ["Today", "My Habits", "AI Coach"]
        nav_cols = st.columns(len(pages))
        for i, p in enumerate(pages):
            # Check if this button is the one the user is currently looking at
            is_active = active_page == p or (p == "Today" and active_page == "Habit Detail")
            label = f"**{p}**" if is_active else p
            
            if nav_cols[i].button(label, key=f"nav_{p}", use_container_width=True):
                st.session_state.active_page = p
                if p != "Today":
                    st.session_state.selected_habit = None
                st.rerun()

    with cols[2]:
        inner_cols = st.columns([1, 2])
        with inner_cols[0]:
            theme_icon = "🌙" if theme == "Dark" else "☀️"
            if st.button(theme_icon, key="theme_toggle", help="Switch theme"):
                st.session_state.theme = "Light" if theme == "Dark" else "Dark"
                st.rerun()
        with inner_cols[1]:
            # Simple progress math
            done_count = sum(1 for h in habits if h.is_completed_today())
            total = len(habits)
            pct = int(done_count / total * 100) if total > 0 else 0
            st.markdown(
                f'<div style="text-align:right;padding-top:8px;">'
                f'<span style="font-size:14px;font-weight:700;color:var(--accent2);">{pct}%</span>'
                f'</div>',
                unsafe_allow_html=True
            )
    
    # Add some breathing room below the fixed nav
    st.markdown('<br><br>', unsafe_allow_html=True)
