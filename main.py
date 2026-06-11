"""
=============================================================================
HABIT.SPACE - Main Application Entry Point
=============================================================================
This is the central hub of the Habit Builder application. It orchestrates:
- Page routing and navigation
- Theme management (Dark/Light mode)
- Data persistence (loading/saving habits)
- UI rendering with celebration effects

Architecture Overview:
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit Frontend                       │
├─────────────────────────────────────────────────────────────┤
│  Navigation Bar  │  Page Content  │  Theme Toggle            │
├─────────────────────────────────────────────────────────────┤
│                    Session State (Data)                      │
├─────────────────────────────────────────────────────────────┤
│  Habits List  │  Active Page  │  Theme  │  Selected Habit   │
└─────────────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────────┐
│                   Business Logic Layer                       │
│  (src/habits.py, src/calendars.py, src/ui_components.py)    │
└─────────────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────────┐
│                   Storage Layer                              │
│  (src/storage.py → data/habits.json)                         │
└─────────────────────────────────────────────────────────────┘

Design Principles:
1. Single Responsibility: Each function does one thing well
2. Fail Gracefully: Handle missing data without crashing
3. Visual Feedback: Celebrate wins, acknowledge effort
4. Smooth Transitions: No jarring page changes
=============================================================================
"""

import streamlit as st
import os
from datetime import date

# ── MODULE IMPORTS ──────────────────────────────────────────────────────────
# Importing from our modular architecture keeps code organized and testable.
from src.habits import Habit, add_habit, delete_habit
from src.storage import load_habits, save_habits
from src.ui_components import (
    render_top_nav,
    glass_card_start,
    glass_card_end,
    rank_badge,
    render_stats_cards,
    celebration_effect,
    motivation_message,
    render_empty_state,
    get_streak_flame_emoji
)
from src.calendars import render_global_calendar, render_habit_calendar, render_streak_visualization


# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION & INITIALIZATION
# ═══════════════════════════════════════════════════════════════════════════

# Configure the Streamlit page with our branding
st.set_page_config(
    page_title="habit.space",      # Browser tab title
    page_icon="🔥",                 # Browser tab icon
    layout="wide",                  # Use full width
    initial_sidebar_state="collapsed"  # Hide sidebar by default
)


# ═══════════════════════════════════════════════════════════════════════════
# DESIGN SYSTEM
# ═══════════════════════════════════════════════════════════════════════════

def apply_design():
    """
    Applies the visual design system to the entire app.
    
    This function:
    1. Sets CSS variables based on current theme
    2. Loads our custom stylesheet
    3. Injects Google Fonts for typography
    4. Applies theme-specific colors and effects
    
    Theme System:
    - Dark Theme: Deep midnight colors with purple accents
    - Light Theme: Clean frosted glass with soft shadows
    
    The CSS variables (--bg, --glass, --text, etc.) are used throughout
    the app for consistent styling that can be changed in one place.
    """
    theme = st.session_state.get("theme", "Dark")
    
    if theme == "Dark":
        # Dark theme: Professional, easy on eyes for night use
        colors = """
        :root {
            --bg: linear-gradient(135deg, #0D0F14 0%, #1A1C25 100%);
            --glass: rgba(25, 28, 38, 0.7);
            --glass-heavy: rgba(15, 17, 23, 0.95);
            --text: #F8FAFC;
            --text2: #94A3B8;
            --text3: #64748B;
            --accent: #7B61FF;
            --accent2: #7B61FF;
            --success: #10B981;
            --danger: #EF4444;
            --warning: #F5A623;
            --border2: rgba(255, 255, 255, 0.1);
            --shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4);
        }
        """
    else:
        # Light theme: Clean, modern, iOS-like frosted glass
        colors = """
        :root {
            --bg: linear-gradient(135deg, #F8FAFC 0%, #E2E8F0 100%);
            --glass: rgba(255, 255, 255, 0.75);
            --glass-heavy: rgba(255, 255, 255, 0.95);
            --text: #1E293B;
            --text2: #64748B;
            --text3: #94A3B8;
            --accent: #6366F1;
            --accent2: #6366F1;
            --success: #10B981;
            --danger: #EF4444;
            --warning: #F5A623;
            --border2: rgba(0, 0, 0, 0.08);
            --shadow: 0 10px 40px 0 rgba(31, 38, 135, 0.07);
        }
        """
    
    # Load external CSS file for additional styling
    try:
        with open("assets/style.css", "r", encoding="utf-8") as f:
            css_code = f.read()
    except FileNotFoundError:
        css_code = ""
        st.warning("CSS file not found. Some styling may be missing.")
    
    # Load Google Fonts for premium typography
    fonts = '''
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    '''
    
    # Inject all styles into the page
    st.html(f"{fonts}<style>{colors}\n{css_code}</style>")


# ═══════════════════════════════════════════════════════════════════════════
# DATA MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════

def init_app():
    """
    Initializes the application state.
    
    This function runs once at app startup and:
    1. Sets default theme preference
    2. Sets default active page
    3. Loads habits from storage into session state
    
    Session state persists across page reruns but clears on browser close,
    which is why we reload from disk each time.
    """
    # Initialize theme preference
    if "theme" not in st.session_state:
        st.session_state.theme = "Dark"
    
    # Initialize page navigation
    if "active_page" not in st.session_state:
        st.session_state.active_page = "Today"
    
    # Initialize selected habit (for detail view)
    if "selected_habit" not in st.session_state:
        st.session_state.selected_habit = None
    
    # Load habits from persistent storage
    if "habits" not in st.session_state:
        raw_habits = load_habits()
        st.session_state.habits = [Habit.from_dict(h) for h in raw_habits]


def save_data():
    """
    Persists current habit data to disk.
    
    Called after any modification to ensure data isn't lost.
    Converts Habit objects to dictionaries for JSON serialization.
    """
    habits_data = [h.to_dict() for h in st.session_state.habits]
    save_habits(habits_data)


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: TODAY (Main Dashboard)
# ═══════════════════════════════════════════════════════════════════════════

def page_today(habits):
    """
    The main dashboard showing today's habits and progress.
    
    This is the "home screen" users see most often. It's designed to:
    1. Show quick stats for motivation
    2. Display monthly activity overview
    3. Provide easy check-in for today's habits
    4. Celebrate completions with visual feedback
    
    Layout:
    ┌──────────────────────────────────────────────┐
    │  Your Progress                               │
    ├──────────────────────────────────────────────┤
    │  [Stats Cards: Total | Completed | Streak]  │
    ├──────────────────────────────────────────────┤
    │  Monthly Activity Calendar                   │
    ├──────────────────────────────────────────────┤
    │  Motivation Message                          │
    ├──────────────────────────────────────────────┤
    │  Today's Tasks                               │
    │  [Habit 1]  [Check-in]  [Details]           │
    │  [Habit 2]  [Check-in]  [Details]           │
    │  [Habit 3]  [Check-in]  [Details]           │
    └──────────────────────────────────────────────┘
    """
    st.markdown("# Your Progress")
    
    # ── Quick Stats ──
    render_stats_cards(habits)
    
    # ── Monthly Activity Calendar ──
    glass_card_start("Monthly Activity", "See your consistency at a glance")
    render_global_calendar(habits)
    glass_card_end()
    
    # ── Motivation Message ──
    if habits:
        total_streak = max((h.get_current_streak() for h in habits), default=0)
        done_count = sum(1 for h in habits if h.is_completed_today())
        rate = (done_count / len(habits) * 100) if habits else 0
        st.markdown(f'''
        <div class="fade-in" style="
            background: var(--glass);
            border: 1px solid var(--border2);
            border-radius: var(--radius-lg);
            padding: var(--space-lg);
            margin: var(--space-lg) 0;
            text-align: center;
        ">
            <p style="font-size: 16px; color: var(--text); margin: 0;">
                {motivation_message(total_streak, rate)}
            </p>
        </div>
        ''', unsafe_allow_html=True)
    
    # ── Today's Tasks List ──
    st.markdown("### Today's Tasks")
    
    if not habits:
        render_empty_state(
            message="No habits yet! Go to 'My Habits' to create your first habit and start your journey.",
            icon="🌟"
        )
    else:
        for h in habits:
            completed = h.is_completed_today()
            streak = h.get_current_streak()
            
            # Three-column layout: Name | Action | Details
            col1, col2, col3 = st.columns([6, 2, 2])
            
            with col1:
                # Habit name with emoji
                status_icon = "✅" if completed else "⬜"
                st.markdown(f"**{status_icon} {h.emoji} {h.name}**")
                if streak > 0:
                    st.caption(f"🔥 {streak} day streak")
            
            with col2:
                if not completed:
                    # Check-in button for incomplete habits
                    if st.button("Check in", key=f"check_{h.name}", 
                                use_container_width=True, type="primary"):
                        h.mark_complete()
                        save_data()
                        # Show celebration effect
                        celebration_effect(h.name)
                        st.rerun()
                else:
                    # Show completed status
                    st.markdown(
                        '<div style="color: var(--success); font-weight: 600; padding: 8px 0;">✓ Done</div>',
                        unsafe_allow_html=True
                    )
            
            with col3:
                # Details button to view habit history
                if st.button("Details", key=f"detail_{h.name}", 
                            use_container_width=True):
                    st.session_state.selected_habit = h.name
                    st.session_state.active_page = "Habit Detail"
                    st.rerun()
            
            st.divider()


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: MY HABITS (Management)
# ═══════════════════════════════════════════════════════════════════════════

def page_manage(habits):
    """
    Habit management page for creating and deleting habits.
    
    Features:
    1. Create new habits with custom emoji and type
    2. View all active habits with their ranks
    3. Delete habits that are no longer needed
    
    The creation form is expanded by default to encourage action.
    """
    st.markdown("# Habit Lab")
    st.caption("Create and manage your habits")
    
    # ── Create New Habit Form ──
    with st.expander("✨ Create New Habit", expanded=True):
        c1, c2, c3 = st.columns([4, 2, 2])
        
        with c1:
            name = st.text_input("What habit do you want to build?", 
                                placeholder="e.g., Morning Meditation")
        
        with c2:
            habit_type = st.selectbox("Type", ["adopt", "quit"], 
                                     help="Adopt = start doing, Quit = stop doing")
        
        with c3:
            emoji = st.selectbox("Icon", [
                "🏃", "📚", "🧘", "💪", "🚭", "📵", 
                "💧", "😴", "🎯", "✍️", "🎨", "🌱"
            ])
        
        # Create button
        if st.button("Create Habit", type="primary", use_container_width=True):
            if not name or not name.strip():
                st.error("Please enter a habit name.")
            else:
                result, error = add_habit(habits, name.strip(), habit_type, emoji)
                if error:
                    st.error(error)
                else:
                    st.success(f"🎉 Habit '{name}' created! Keep the streak going!")
                    save_data()
                    st.rerun()
    
    # ── Active Habits List ──
    st.markdown("### Active Habits")
    
    if not habits:
        st.info("No habits yet. Create your first one above!")
    else:
        for h in habits:
            rank = h.get_rank()
            streak = h.get_current_streak()
            
            c1, c2 = st.columns([8, 2])
            
            with c1:
                # Habit info with rank badge
                st.markdown(f"**{h.emoji} {h.name}**")
                st.caption(f"{rank_badge(rank, text_only=True)} • {streak} day streak")
            
            with c2:
                # Delete button (with confirmation)
                if st.button("Remove", key=f"del_{h.name}", type="secondary"):
                    delete_habit(habits, h.name)
                    st.success(f"Removed '{h.name}'")
                    save_data()
                    st.rerun()
            
            st.divider()


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: HABIT DETAIL (Deep Dive)
# ═══════════════════════════════════════════════════════════════════════════

def page_detail(habits, name):
    """
    Detailed view for a single habit.
    
    Shows comprehensive statistics and history:
    1. Monthly calendar with completion history
    2. Current and longest streaks
    3. Completion rate
    4. Visual streak timeline
    
    This view helps users understand their patterns and stay motivated.
    """
    habit = next((h for h in habits if h.name == name), None)
    if not habit:
        st.error("Habit not found.")
        return
    
    # Back button
    if st.button("← Back to Dashboard"):
        st.session_state.active_page = "Today"
        st.rerun()
    
    # ── Habit Header ──
    st.markdown(f"# {habit.emoji} {habit.name}")
    
    # ── Quick Stats ──
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Current Streak", f"{habit.get_current_streak()} 🔥")
    c2.metric("Longest Streak", f"{habit.get_longest_streak()} 🏆")
    c3.metric("Total Completions", f"{habit.get_total_completions()} ✓")
    c4.metric("30-Day Rate", f"{habit.get_completion_rate(30)}%")
    
    # ── Monthly Calendar ──
    glass_card_start(f"{habit.emoji} Progress History")
    render_habit_calendar(habit)
    glass_card_end()
    
    # ── Streak Visualization ──
    glass_card_start("Last 30 Days")
    render_streak_visualization(habit)
    glass_card_end()
    
    # ── Rank Display ──
    rank = habit.get_rank()
    st.markdown(f"### Current Rank")
    st.markdown(f'''
    <div style="
        background: var(--glass);
        border: 1px solid {rank["color"]}44;
        border-radius: var(--radius-xl);
        padding: var(--space-lg);
        text-align: center;
        margin: var(--space-lg) 0;
    ">
        <div style="font-size: 48px; margin-bottom: 8px;">{rank["icon"]}</div>
        <div style="font-size: 24px; font-weight: 700; color: {rank["color"]};">
            {rank["label"]}
        </div>
        <div style="font-size: 14px; color: var(--text2); margin-top: 8px;">
            Streak: {habit.get_current_streak()} days
        </div>
    </div>
    ''', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: AI COACH (Placeholder)
# ═══════════════════════════════════════════════════════════════════════════

def page_coach():
    """
    AI Coach page (coming soon).
    
    Future feature: AI-powered habit recommendations and insights.
    """
    st.markdown("# AI Coach")
    st.info("🤖 Your personal habit coach is resting. Coming back soon with personalized insights!")
    
    glass_card_start("What to expect")
    st.markdown("""
    - **Personalized Tips**: Get advice based on your patterns
    - **Optimal Timing**: Learn when you're most likely to succeed
    - **Smart Reminders**: Notifications that actually help
    - **Progress Insights**: Understand what's working and what's not
    """)
    glass_card_end()


# ═══════════════════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════════════════

def main():
    """
    Main application entry point.
    
    Execution flow:
    1. Initialize app state and load data
    2. Apply visual design system
    3. Render navigation bar
    4. Route to appropriate page based on active_page
    """
    # Step 1: Initialize
    init_app()
    
    # Step 2: Apply design
    apply_design()
    
    # Step 3: Render navigation
    render_top_nav(
        st.session_state.habits,
        st.session_state.active_page,
        st.session_state.theme
    )
    
    # Step 4: Route to page
    habits = st.session_state.habits
    active = st.session_state.active_page
    
    # Centered content area (with side margins)
    _, stage, _ = st.columns([1, 10, 1])
    with stage:
        if active == "Today":
            page_today(habits)
        elif active == "My Habits":
            page_manage(habits)
        elif active == "Habit Detail":
            page_detail(habits, st.session_state.get("selected_habit"))
        elif active == "AI Coach":
            page_coach()
        else:
            # Fallback for unknown pages
            st.error("Page not found.")


# ═══════════════════════════════════════════════════════════════════════════
# APPLICATION STARTUP
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    main()