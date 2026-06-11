"""
=============================================================================
HABIT.SPACE - Main Application Entry Point (Game Edition)
=============================================================================
This is the central hub of the Habit Builder application. It orchestrates:
- User authentication (login/register)
- Page routing and navigation
- Theme management (Dark/Light mode)
- Data persistence (loading/saving habits)
- UI rendering with celebration effects
- Gamification features (XP, levels, rankings, events)

Architecture Overview:
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit Frontend                       │
├─────────────────────────────────────────────────────────────┤
│  Auth Screen  │  Navigation Bar  │  Theme Toggle             │
├─────────────────────────────────────────────────────────────┤
│                    Session State (Data)                      │
├─────────────────────────────────────────────────────────────┤
│  User  │  Habits List  │  Active Page  │  Theme  │  Events  │
└─────────────────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│                   Business Logic Layer                       │
│  (src/habits.py, src/auth.py, src/calendars.py,            │
│   src/ui_components.py)                                      │
└─────────────────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│                   Storage Layer                              │
│  (src/storage.py → data/habits.json, data/users.json)       │
└─────────────────────────────────────────────────────────────┘

Design Principles:
1. Single Responsibility: Each function does one thing well
2. Fail Gracefully: Handle missing data without crashing
3. Visual Feedback: Celebrate wins, acknowledge effort
4. Gamification: Make habit building feel like a game
=============================================================================
"""

import streamlit as st
import os
from datetime import date

# ── MODULE IMPORTS ──────────────────────────────────────────────────────────
from src.habits import Habit, add_habit, delete_habit
from src.storage import load_habits, save_habits
from src.i18n import translate, set_language
from src.ai import get_habit_recommendations, call_ollama
from src.auth import (
    User, Event,
    register_user, login_user, get_user_by_username, update_user,
    load_events, save_events, get_global_rankings, get_user_rank_position,
    check_achievements, ACHIEVEMENTS,
    XP_HABIT_COMPLETION, XP_STREAK_BONUS
)
from src.ui_components import render_top_nav, render_ai_companion, glass_card_start, glass_card_end, rank_badge, render_stats_cards, celebration_effect, motivation_message, render_empty_state, get_streak_flame_emoji
from src.calendars import render_global_calendar, render_habit_calendar, render_streak_visualization


# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION & INITIALIZATION
# ═══════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="habit.space - Game Edition",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ═══════════════════════════════════════════════════════════════════════════
# DESIGN SYSTEM
# ═══════════════════════════════════════════════════════════════════════════

def apply_design():
    """
    Applies the visual design system to the entire app.
    """
    theme = st.session_state.get("theme", "Dark")
    
    css_files = ["assets/style.css"]
    if theme == "Retro":
        css_files.append("assets/retro.css")
        
    css_code = ""
    for file in css_files:
        try:
            with open(file, "r", encoding="utf-8") as f:
                css_code += f.read() + "\n"
        except FileNotFoundError:
            pass
    
    theme_attr = f'data-theme="{theme.lower()}"'
    
    st.markdown(f'''
    <div {theme_attr}>
    <style>{css_code}</style>
    ''', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# DATA MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════

def init_app():
    """Initialize the application state."""
    if "theme" not in st.session_state:
        st.session_state.theme = "Dark"
    
    if "active_page" not in st.session_state:
        st.session_state.active_page = "Today"
    
    if "selected_habit" not in st.session_state:
        st.session_state.selected_habit = None
    
    if "habits" not in st.session_state:
        if st.session_state.current_user:
            raw_habits = load_habits(st.session_state.current_user.username)
            st.session_state.habits = [Habit.from_dict(h) for h in raw_habits]
        else:
            st.session_state.habits = []
    
    if "current_user" not in st.session_state:
        st.session_state.current_user = None


def save_data():
    """Persist habit data to MongoDB."""
    if st.session_state.current_user:
        habits_data = [h.to_dict() for h in st.session_state.habits]
        save_habits(st.session_state.current_user.username, habits_data)


def save_user_data():
    """Persist user data to disk."""
    if st.session_state.current_user:
        update_user(st.session_state.current_user)


# ═══════════════════════════════════════════════════════════════════════════
# AUTHENTICATION PAGES
# ═══════════════════════════════════════════════════════════════════════════

def page_login():
    """Login/Register page."""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 32px;">
            <h1 style="font-size: 42px; margin: 0; font-family:'Space Grotesk', sans-serif;">
                habit<span style="color:var(--accent2);">.space</span>
            </h1>
            <p style="color: var(--text2); font-size: 18px; margin-top: 8px;">
                🎮 Level up your life, one habit at a time
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔑 Login", "✨ Register"])
        
        with tab1:
            login_username = st.text_input("Username", key="login_user", 
                                          placeholder="Enter your username")
            login_password = st.text_input("Password", key="login_pass", 
                                          type="password", placeholder="Enter your password")
            
            if st.button("Login", type="primary", use_container_width=True):
                user, error = login_user(login_username, login_password)
                if user:
                    st.session_state.current_user = user
                    st.session_state.active_page = "Today"
                    st.rerun()
                else:
                    st.error(error)
            
            st.markdown("<div style='text-align: center; margin: 16px 0;'>OR</div>", unsafe_allow_html=True)
            if st.button("Login with Google", use_container_width=True):
                st.info("Google Login integration is coming soon! Please use local login for now.")
        
        with tab2:
            reg_username = st.text_input("Choose Username", key="reg_user",
                                        placeholder="Pick a unique username")
            reg_password = st.text_input("Password", key="reg_pass",
                                        type="password", placeholder="At least 4 characters")
            reg_confirm = st.text_input("Confirm Password", key="reg_confirm",
                                       type="password", placeholder="Confirm your password")
            
            if st.button("Create Account", type="primary", use_container_width=True):
                if reg_password != reg_confirm:
                    st.error("Passwords do not match!")
                else:
                    user, error = register_user(reg_username, reg_password)
                    if user:
                        st.success("Account created! Please login.")
                    else:
                        st.error(error)


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: TODAY (Main Dashboard)
# ═══════════════════════════════════════════════════════════════════════════

def page_today(habits, user: User):
    """The main dashboard with game-like features."""
    # ── User Status Bar ──
    render_user_status_bar(user)
    
    st.markdown("# Your Progress")
    
    # ── Quick Stats ──
    render_stats_cards(habits)
    
    # ── XP & Level Progress ──
    render_xp_progress(user)
    
    # ── User Parameters ──
    render_user_parameters(user)
    
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
            
            col1, col2, col3 = st.columns([6, 2, 2])
            
            with col1:
                status_icon = "✅" if completed else "⬜"
                st.markdown(f"**{status_icon} {h.emoji} {h.name}**")
                if streak > 0:
                    st.caption(f"🔥 {streak} day streak")
            
            with col2:
                if not completed:
                    if st.button("Check in", key=f"check_{h.name}", 
                                use_container_width=True, type="primary"):
                        h.mark_complete()
                        # Award XP
                        xp_earned = XP_HABIT_COMPLETION
                        if streak > 0:
                            xp_earned += XP_STREAK_BONUS
                        user.add_xp(xp_earned)
                        user.total_completions += 1
                        user.update_parameters(habits)
                        
                        # Check achievements
                        new_achievements = check_achievements(user, habits)
                        
                        save_data()
                        save_user_data()
                        
                        # Show celebration
                        celebration_effect(f"{h.name} (+{xp_earned} XP)")
                        
                        if new_achievements:
                            for ach_id in new_achievements:
                                ach = ACHIEVEMENTS[ach_id]
                                st.toast(f"🏆 Achievement Unlocked: {ach['icon']} {ach['name']}!")
                        
                        st.rerun()
                else:
                    st.markdown(
                        '<div style="color: var(--success); font-weight: 600; padding: 8px 0;">✓ Done</div>',
                        unsafe_allow_html=True
                    )
            
            with col3:
                if st.button("Details", key=f"detail_{h.name}", 
                            use_container_width=True):
                    st.session_state.selected_habit = h.name
                    st.session_state.active_page = "Habit Detail"
                    st.rerun()
            
            st.divider()


def render_user_status_bar(user: User):
    """Render the user status bar with level, XP, and rank."""
    rank_info = user.get_rank_info()
    
    st.markdown(f'''
    <div style="
        background: var(--glass);
        border: 1px solid {rank_info['color']}44;
        border-radius: var(--radius-xl);
        padding: var(--space-md) var(--space-lg);
        margin-bottom: var(--space-lg);
        display: flex;
        align-items: center;
        justify-content: space-between;
    ">
        <div style="display: flex; align-items: center; gap: 12px;">
            <span style="font-size: 28px;">{rank_info['icon']}</span>
            <div>
                <div style="font-size: 14px; font-weight: 700; color: {rank_info['color']};">
                    Level {user.level} • {user.title}
                </div>
                <div style="font-size: 12px; color: var(--text2);">
                    {user.xp} / {user.xp_to_next_level} XP
                </div>
            </div>
        </div>
        <div style="text-align: right;">
            <div style="font-size: 12px; color: var(--text2);">Global Rank</div>
            <div style="font-size: 20px; font-weight: 700; color: var(--text);">
                #{get_user_rank_position(user.username) or '—'}
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)


def render_xp_progress(user: User):
    """Render XP progress bar."""
    progress = user.xp_progress * 100
    st.markdown(f'''
    <div style="margin: var(--space-md) 0;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
            <span style="font-size: 12px; color: var(--text2);">XP Progress</span>
            <span style="font-size: 12px; color: var(--text2);">{user.xp}/{user.xp_to_next_level}</span>
        </div>
        <div style="
            width: 100%;
            height: 8px;
            background: rgba(128, 128, 128, 0.2);
            border-radius: var(--radius-full);
            overflow: hidden;
        ">
            <div style="
                width: {progress}%;
                height: 100%;
                background: linear-gradient(90deg, var(--accent2), #6366F1);
                border-radius: var(--radius-full);
                transition: width 0.5s ease;
            "></div>
        </div>
    </div>
    ''', unsafe_allow_html=True)


def render_user_parameters(user: User):
    """Render user parameter stats as a game dashboard."""
    glass_card_start("📊 Character Stats", "Your habit-building attributes")
    
    params = [
        ("💪 Discipline", user.discipline, "How consistent you are with daily habits"),
        ("🔄 Consistency", user.consistency, "Your streak maintenance ability"),
        ("🎯 Dedication", user.dedication, "Total effort and time invested"),
        ("🧠 Focus", user.focus, "Completion rate across all habits"),
    ]
    
    for name, value, desc in params:
        color = "#10B981" if value >= 70 else "#F5A623" if value >= 40 else "#EF4444"
        st.markdown(f'''
        <div style="margin-bottom: 16px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                <span style="font-size: 14px; font-weight: 600; color: var(--text);">{name}</span>
                <span style="font-size: 14px; font-weight: 700; color: {color};">{value}</span>
            </div>
            <div style="font-size: 11px; color: var(--text3); margin-bottom: 6px;">{desc}</div>
            <div style="
                width: 100%;
                height: 6px;
                background: rgba(128, 128, 128, 0.15);
                border-radius: var(--radius-full);
                overflow: hidden;
            ">
                <div style="
                    width: {value}%;
                    height: 100%;
                    background: {color};
                    border-radius: var(--radius-full);
                    transition: width 0.5s ease;
                "></div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    glass_card_end()


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: MY HABITS (Management)
# ═══════════════════════════════════════════════════════════════════════════

def page_manage(habits, user: User):
    """Habit management page."""
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
        
        if st.button("Create Habit", type="primary", use_container_width=True):
            if not name or not name.strip():
                st.error("Please enter a habit name.")
            else:
                result, error = add_habit(habits, name.strip(), habit_type, emoji)
                if error:
                    st.error(error)
                else:
                    user.habits_created += 1
                    user.add_xp(25)  # Bonus XP for creating a habit
                    check_achievements(user, habits)
                    st.success(f"🎉 Habit '{name}' created! (+25 XP)")
                    save_data()
                    save_user_data()
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
                st.markdown(f"**{h.emoji} {h.name}**")
                st.caption(f"{rank_badge(rank, text_only=True)} • {streak} day streak")
            
            with c2:
                if st.button("Remove", key=f"del_{h.name}", type="secondary"):
                    delete_habit(habits, h.name)
                    st.success(f"Removed '{h.name}'")
                    save_data()
                    st.rerun()
            
            st.divider()


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: HABIT DETAIL
# ═══════════════════════════════════════════════════════════════════════════

def page_detail(habits, name):
    """Detailed view for a single habit."""
    habit = next((h for h in habits if h.name == name), None)
    if not habit:
        st.error("Habit not found.")
        return
    
    if st.button("← Back to Dashboard"):
        st.session_state.active_page = "Today"
        st.rerun()
    
    st.markdown(f"# {habit.emoji} {habit.name}")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Current Streak", f"{habit.get_current_streak()} 🔥")
    c2.metric("Longest Streak", f"{habit.get_longest_streak()} 🏆")
    c3.metric("Total Completions", f"{habit.get_total_completions()} ✓")
    c4.metric("30-Day Rate", f"{habit.get_completion_rate(30)}%")
    
    glass_card_start(f"{habit.emoji} Progress History")
    render_habit_calendar(habit)
    glass_card_end()
    
    glass_card_start("Last 30 Days")
    render_streak_visualization(habit)
    glass_card_end()
    
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
# PAGE: EVENTS (Challenges)
# ═══════════════════════════════════════════════════════════════════════════

def page_events(user: User):
    """Events/Challenges page."""
    st.markdown("# 🎯 Challenges & Events")
    st.caption("Join community challenges to level up faster!")
    
    events = load_events()
    
    # ── Active Events ──
    st.markdown("### Active Challenges")
    
    active_events = [e for e in events if e.is_active]
    
    if not active_events:
        st.info("No active events at the moment. Check back soon!")
    else:
        for event in active_events:
            is_joined = event.id in user.joined_events
            is_completed = event.id in user.completed_events
            
            glass_card_start(f"{event.emoji} {event.name}")
            
            st.markdown(f"**{event.description}**")
            st.caption(f"📅 {event.start_date} to {event.end_date}")
            st.caption(f"🏆 Reward: {event.xp_reward} XP")
            st.caption(f"📝 Suggested habit: {event.habit_suggestion}")
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                if is_completed:
                    st.success("✅ Completed! Reward claimed!")
                elif is_joined:
                    st.info("🔄 In Progress - Keep going!")
            
            with col2:
                if not is_joined and not is_completed:
                    if st.button("Join Challenge", key=f"join_{event.id}", 
                                type="primary", use_container_width=True):
                        user.joined_events.append(event.id)
                        user.events_joined += 1
                        user.add_xp(25)  # Bonus for joining
                        check_achievements(user)
                        update_user(user)
                        save_events(events)
                        st.success(f"Joined! +25 XP")
                        st.rerun()
            
            glass_card_end()
    
    # ── Completed Events ──
    if user.completed_events:
        st.markdown("### Completed Challenges")
        for event in events:
            if event.id in user.completed_events:
                st.markdown(f"✅ **{event.name}** - {event.xp_reward} XP earned")


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: RANKINGS (Leaderboard)
# ═══════════════════════════════════════════════════════════════════════════

def page_rankings(user: User):
    """Global rankings/leaderboard page."""
    st.markdown("# 🏆 Global Rankings")
    st.caption("See where you stand among habit builders!")
    
    # ── User's Rank ──
    user_position = get_user_rank_position(user.username)
    rank_info = user.get_rank_info()
    
    st.markdown(f'''
    <div style="
        background: var(--glass);
        border: 2px solid {rank_info['color']};
        border-radius: var(--radius-xl);
        padding: var(--space-lg);
        margin-bottom: var(--space-xl);
        text-align: center;
    ">
        <div style="font-size: 48px; margin-bottom: 8px;">{rank_info['icon']}</div>
        <div style="font-size: 14px; color: var(--text2);">Your Global Rank</div>
        <div style="font-size: 36px; font-weight: 700; color: {rank_info['color']};">
            #{user_position if user_position > 0 else '—'}
        </div>
        <div style="font-size: 18px; color: var(--text); margin-top: 8px;">
            Level {user.level} • {user.title}
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    # ── Leaderboard ──
    rankings = get_global_rankings(10)
    
    glass_card_start("Top Players")
    
    for rank_num, player in rankings:
        player_rank = player.get_rank_info()
        is_current_user = player.username == user.username
        
        bg_style = ""
        if rank_num == 1:
            bg_style = "background: rgba(255, 215, 0, 0.1);"
        elif rank_num == 2:
            bg_style = "background: rgba(192, 192, 192, 0.1);"
        elif rank_num == 3:
            bg_style = "background: rgba(205, 127, 50, 0.1);"
        elif is_current_user:
            bg_style = "background: rgba(123, 97, 255, 0.1);"
        
        st.markdown(f'''
        <div style="
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 16px;
            border-radius: var(--radius-lg);
            margin-bottom: 8px;
            {bg_style}
            border: 1px solid {'var(--accent2)' if is_current_user else 'var(--border2)'};
        ">
            <div style="font-size: 20px; font-weight: 700; color: var(--text); width: 30px;">
                {'🥇' if rank_num == 1 else '🥈' if rank_num == 2 else '🥉' if rank_num == 3 else f'#{rank_num}'}
            </div>
            <div style="font-size: 24px;">{player_rank['icon']}</div>
            <div style="flex: 1;">
                <div style="font-weight: 600; color: var(--text);">
                    {player.username}
                    {'(You)' if is_current_user else ''}
                </div>
                <div style="font-size: 12px; color: var(--text2);">
                    {player.title} • Level {player.level}
                </div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 16px; font-weight: 700; color: var(--accent2);">
                    {player.xp} XP
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    glass_card_end()
    
    # ── Total Players ──
    total_players = len(get_global_rankings(9999))
    st.caption(f"Total players: {total_players}")


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: ACHIEVEMENTS
# ═══════════════════════════════════════════════════════════════════════════

def page_achievements(user: User):
    """Achievements page."""
    st.markdown("# 🏆 Achievements")
    st.caption("Badges you've earned on your journey")
    
    # Check for new achievements
    new_achievements = check_achievements(user, st.session_state.habits)
    if new_achievements:
        for ach_id in new_achievements:
            ach = ACHIEVEMENTS[ach_id]
            st.success(f"🎉 New Achievement: {ach['icon']} {ach['name']}!")
        save_user_data()
    
    # ── Earned Achievements ──
    st.markdown("### Earned")
    
    earned_count = 0
    for ach_id, ach in ACHIEVEMENTS.items():
        if ach_id in user.achievements:
            earned_count += 1
            glass_card_start(f"{ach['icon']} {ach['name']}")
            st.markdown(f"*{ach['description']}*")
            st.caption(f"Reward: {ach['xp_reward']} XP")
            glass_card_end()
    
    if earned_count == 0:
        st.info("No achievements yet. Keep building habits to earn badges!")
    
    # ── Locked Achievements ──
    st.markdown("### Locked")
    
    locked_count = 0
    for ach_id, ach in ACHIEVEMENTS.items():
        if ach_id not in user.achievements:
            locked_count += 1
            st.markdown(f"""
            <div style="
                opacity: 0.4;
                padding: 12px 16px;
                margin-bottom: 8px;
                border: 1px solid var(--border2);
                border-radius: var(--radius-lg);
            ">
                <div style="font-size: 20px; font-weight: 600; color: var(--text);">
                    🔒 {ach['name']}
                </div>
                <div style="font-size: 13px; color: var(--text2);">
                    {ach['description']}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.caption(f"Progress: {earned_count}/{len(ACHIEVEMENTS)} achievements earned")


# ═══════════════════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════════════════

def main():
    """Main application entry point."""
    init_app()
    apply_design()
    
    # Check if user is logged in
    if st.session_state.current_user is None:
        page_login()
        return
    
    user = st.session_state.current_user
    habits = st.session_state.habits
    active = st.session_state.active_page
    
    # ── Render Navigation ──
    render_top_nav(habits, active, st.session_state.theme)
    render_ai_companion(user.to_dict())
    
    # ── Route to Page ──
    _, stage, _ = st.columns([1, 10, 1])
    with stage:
        if active == "Today":
            page_today(habits, user)
        elif active == "My Habits":
            page_manage(habits, user)
        elif active == "Habit Detail":
            page_detail(habits, st.session_state.get("selected_habit"))
        elif active == "Events":
            page_events(user)
        elif active == "Rankings":
            page_rankings(user)
        elif active == "Achievements":
            page_achievements(user)
        elif active == "AI Coach":
            page_ai_coach(user)
        else:
            st.error("Page not found.")


def page_ai_coach(user: User):
    """AI Coach page for recommendations and motivation."""
    st.markdown(f"# 🤖 {translate('ai_coach')}")
    st.caption("Personalized missions from your Cyber-Buddy")
    
    glass_card_start("✨ Habit Discovery Survey", "Answer these to get personalized missions")
    
    with st.form("ai_survey"):
        q1 = st.text_area("What are your primary goals for the next 30 days?", placeholder="e.g., Learn Python, lose weight, read more...")
        q2 = st.selectbox("How much time can you dedicate daily?", ["< 15 mins", "15-30 mins", "30-60 mins", "1 hour+"])
        q3 = st.multiselect("What areas do you want to improve?", ["Health", "Productivity", "Mindfulness", "Learning", "Social"])
        
        submitted = st.form_submit_button("Generate Missions", type="primary")
        if submitted:
            user_answers = {"goals": q1, "time": q2, "areas": q3}
            with st.spinner("Cyber-Buddy is calculating your path..."):
                recommendations = get_habit_recommendations(user_answers)
                st.session_state.ai_recommendations = recommendations
            st.rerun()
    
    glass_card_end()
    
    if "ai_recommendations" in st.session_state:
        glass_card_start("⚡ Your Cyber-Missions", "Based on your bio-readings")
        st.markdown(st.session_state.ai_recommendations)
        if st.button("Clear Recommendations"):
            del st.session_state.ai_recommendations
            st.rerun()
        glass_card_end()

if __name__ == "__main__":
    main()