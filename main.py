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
import hashlib
from datetime import date
try:
    from streamlit_echarts import st_echarts
except ImportError:
    st_echarts = None

# ── MODULE IMPORTS ──────────────────────────────────────────────────────────
from src.habits import Habit, add_habit, delete_habit
from src.storage import load_habits, save_habit, delete_habit as db_delete_habit
from src.i18n import t, render_language_selector, set_active_language, DEFAULT_LANGUAGE
from src.auth import (
    User, Event,
    register_user, login_user, get_user_by_username, update_user,
    get_google_oauth_url, login_with_google_code, apply_onboarding_profile,
    load_events, save_events, get_global_rankings, get_user_rank_position,
    check_achievements, ACHIEVEMENTS,
    XP_HABIT_COMPLETION, XP_STREAK_BONUS
)
from src.ui_components import (
    render_top_nav,
    glass_card_start,
    glass_card_end,
    rank_badge,
    render_stats_cards,
    celebration_effect,
    motivation_message,
    render_empty_state,
    get_streak_flame_emoji,
    streak_display,
    habit_card,
    progress_ring,
)
from src.calendars import render_global_calendar, render_habit_calendar, render_streak_visualization
from src.companion_widget import render_companion


CATEGORIES = {
    "health": "❤️ Health",
    "lifestyle": "🏡 Lifestyle",
    "finance": "💰 Finance",
    "learning": "📚 Learning",
    "productivity": "⏱️ Productivity",
    "mindfulness": "🧘 Mindfulness",
    "creativity": "🎨 Creativity"
}

def guess_category(name: str) -> str:
    name_lower = name.lower()
    if any(w in name_lower for w in ["run", "walk", "exercise", "gym", "workout", "water", "drink", "sleep", "eat", "food", "health", "stretch", "jog", "meds", "vitamin", "diet", "healthy"]):
        return "health"
    if any(w in name_lower for w in ["clean", "wake", "bed", "cook", "wash", "shower", "routine", "house", "garden", "dog", "cat", "pet", "habit", "lifestyle", "read news", "social", "talk", "message", "chat", "friend", "call"]):
        return "lifestyle"
    if any(w in name_lower for w in ["money", "save", "finance", "budget", "spend", "expense", "invest", "stock", "portfolio", "crypto", "pay", "bill"]):
        return "finance"
    if any(w in name_lower for w in ["read", "study", "learn", "book", "course", "practice", "skill", "write code", "programming", "math", "history", "languages", "vocab", "class", "lecture"]):
        return "learning"
    if any(w in name_lower for w in ["work", "focus", "productivity", "plan", "organize", "todo", "schedule", "task", "email", "inbox", "project", "meeting"]):
        return "productivity"
    if any(w in name_lower for w in ["meditate", "breathe", "breathing", "mindful", "journal", "reflect", "gratitude", "calm", "relax", "yoga"]):
        return "mindfulness"
    if any(w in name_lower for w in ["paint", "draw", "creativity", "write", "music", "guitar", "piano", "sing", "craft", "photo", "video", "code project", "design", "hobby"]):
        return "creativity"
    return "lifestyle"  # default

STARTER_HABITS = {
    "Health and energy": [
        ("Drink water after waking", "adopt", "health"),
        ("10 minute walk", "adopt", "health"),
    ],
    "Learning and skills": [
        ("Read 10 pages", "adopt", "learning"),
        ("Practice one skill block", "adopt", "learning"),
    ],
    "Mindfulness": [
        ("2 minute breathing reset", "adopt", "mindfulness"),
        ("Write one reflection", "adopt", "mindfulness"),
    ],
    "Productivity": [
        ("Plan top 3 tasks", "adopt", "productivity"),
        ("No phone first 20 minutes", "quit", "productivity"),
    ],
    "Creativity": [
        ("Make one small thing", "adopt", "creativity"),
        ("Capture one idea", "adopt", "creativity"),
    ],
    "Social confidence": [
        ("Send one thoughtful message", "adopt", "lifestyle"),
        ("Start one small conversation", "adopt", "lifestyle"),
    ],
}


ONBOARDING_STEPS = [
    {
        "key": "identity",
        "title": "What feels most like your current style?",
        "subtitle": "Pick the one that sounds closest. This sets the first shape of your traits.",
        "options": [
            "I follow a plan and like checking things off",
            "I get bursts of energy and enjoy experimenting",
            "I am steady when the system is simple",
            "I restart well after missing days",
        ],
        "mode": "single",
    },
    {
        "key": "motivation",
        "title": "What usually keeps you moving?",
        "subtitle": "Choose the strongest signal. You can refine this later through your habits.",
        "options": ["Clear targets", "Variety and novelty", "Accountability", "A calm routine"],
        "mode": "single",
    },
    {
        "key": "energy",
        "title": "When is your energy easiest to use?",
        "subtitle": "This helps the companion time its encouragement style.",
        "options": ["Morning", "Afternoon", "Evening", "Late night"],
        "mode": "single",
    },
    {
        "key": "motivation_style",
        "title": "How should your companion talk to you?",
        "subtitle": "This changes praise, reminders, and check-in messages.",
        "options": ["Gentle encouragement", "Direct challenge", "Playful praise", "Quiet reminders"],
        "mode": "single",
    },
    {
        "key": "focus_areas",
        "title": "What do you want to grow first?",
        "subtitle": "Choose a few areas so your starter habits feel relevant.",
        "options": [
            "Health and energy",
            "Learning and skills",
            "Mindfulness",
            "Productivity",
            "Creativity",
            "Social confidence",
        ],
        "mode": "multi",
    },
]


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
    
    # Load base style
    try:
        with open("assets/style.css", "r", encoding="utf-8") as f:
            base_css = f.read()
    except FileNotFoundError:
        base_css = ""
        
    # Load retro style if needed
    retro_css = ""
    if theme == "Retro":
        try:
            with open("assets/retro.css", "r", encoding="utf-8") as f:
                retro_css = f.read()
        except FileNotFoundError:
            pass
    
    st.markdown(f'''
    <style>
    {base_css}
    {retro_css}
    </style>
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
    
    if "current_user" not in st.session_state:
        st.session_state.current_user = None
    
    if "habits" not in st.session_state:
        if st.session_state.current_user:
            raw_habits = load_habits(st.session_state.current_user.username)
            st.session_state.habits = [Habit.from_dict(h) for h in raw_habits]
        else:
            st.session_state.habits = []

    if "oauth_checked" not in st.session_state:
        st.session_state.oauth_checked = False

    if "onboarding_completed" not in st.session_state:
        st.session_state.onboarding_completed = False

    set_active_language(st.session_state.get("app_language", DEFAULT_LANGUAGE))


def save_data():
    """Persist habit data to Supabase."""
    if st.session_state.current_user:
        username = st.session_state.current_user.username
        for habit in st.session_state.habits:
            save_habit(username, habit.to_dict())


def save_user_data():
    """Persist user data to disk."""
    if st.session_state.current_user:
        update_user(st.session_state.current_user)


def set_logged_in_user(user: User):
    """Store the active user and load that user's habits."""
    st.session_state.current_user = user
    raw_habits = load_habits(user.username)
    st.session_state.habits = [Habit.from_dict(h) for h in raw_habits]
    st.session_state.active_page = "Today"


def handle_google_oauth_callback():
    """Complete Google OAuth when Supabase redirects back with a code."""
    raw_params = dict(st.query_params) if hasattr(st, "query_params") else {}
    code = raw_params.get("code") or ""
    if isinstance(code, list):
        code = code[0] if code else ""

    if not code:
        return

    # If we already have a user, do nothing
    if st.session_state.get("user"):
        st.query_params.clear()
        return

    # Process the exchange
    user, error = login_with_google_code(code)
    
    # Always clear the query params to prevent re-processing the same code
    try:
        st.query_params.clear()
    except Exception:
        pass

    if user:
        set_logged_in_user(user)
        st.rerun()
    else:
        st.error(f"OAuth Error: {error}")


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
                {t('app.subtitle')}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs([t("auth.login"), t("auth.register")])
        
        with tab1:
            login_username = st.text_input(t("auth.username"), key="login_user", 
                                          placeholder="Enter your username")
            login_password = st.text_input(t("auth.password"), key="login_pass", 
                                          type="password", placeholder="Enter your password")
            
            if st.button(t("auth.login_button"), type="primary", use_container_width=True):
                user, error = login_user(login_username, login_password)
                if user:
                    set_logged_in_user(user)
                    st.rerun()
                else:
                    st.error(error)
            
            st.markdown(f"<div style='text-align: center; margin: 16px 0;'>{t('auth.or')}</div>", unsafe_allow_html=True)
            google_url, google_error = get_google_oauth_url()
            if google_url:
                st.link_button(t("auth.google_button"), google_url, use_container_width=True)
            else:
                st.warning(google_error)
        
        with tab2:
            reg_username = st.text_input(t("auth.username"), key="reg_user",
                                        placeholder="Pick a unique username")
            reg_password = st.text_input(t("auth.password"), key="reg_pass",
                                        type="password", placeholder="At least 4 characters")
            reg_confirm = st.text_input(t("auth.confirm_password"), key="reg_confirm",
                                       type="password", placeholder="Confirm your password")
            
            if st.button(t("auth.register_button"), type="primary", use_container_width=True):
                if reg_password != reg_confirm:
                    st.error(t("auth.passwords_do_not_match"))
                elif not reg_username.strip():
                    st.error(t("auth.username_empty"))
                elif len(reg_password) < 4:
                    st.error(t("auth.password_too_short"))
                else:
                    user, error = register_user(reg_username, reg_password)
                    if user:
                        set_logged_in_user(user)
                        st.success(t("auth.account_created"))
                        st.rerun()
                    else:
                        st.error(error)


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: ONBOARDING QUIZ
# ═══════════════════════════════════════════════════════════════════════════

def page_onboarding(user: User):
    """First-run quiz that builds the user's trait profile one step at a time."""
    if "onboarding_step" not in st.session_state:
        st.session_state.onboarding_step = 0
    if "onboarding_answers" not in st.session_state:
        st.session_state.onboarding_answers = {}

    total_steps = len(ONBOARDING_STEPS) + 2
    step_index = st.session_state.onboarding_step
    progress = min((step_index + 1) / total_steps, 1.0)

    st.markdown("# Personal Setup")
    st.progress(progress)
    st.caption(f"Step {step_index + 1} of {total_steps}")

    if step_index < len(ONBOARDING_STEPS):
        _render_onboarding_choice_step(ONBOARDING_STEPS[step_index])
        return

    if step_index == len(ONBOARDING_STEPS):
        _render_starter_habit_step()
        return

    _render_companion_name_step(user)


def _render_onboarding_choice_step(step: dict):
    answers = st.session_state.onboarding_answers
    selected = answers.get(step["key"], [] if step["mode"] == "multi" else None)

    st.markdown(f"## {step['title']}")
    st.caption(step["subtitle"])

    for option in step["options"]:
        is_selected = option in selected if isinstance(selected, list) else option == selected
        label = f"{'✓ ' if is_selected else ''}{option}"
        if st.button(label, key=f"quiz_{step['key']}_{option}", use_container_width=True):
            if step["mode"] == "multi":
                selected_values = list(selected or [])
                if option in selected_values:
                    selected_values.remove(option)
                else:
                    selected_values.append(option)
                answers[step["key"]] = selected_values
            else:
                answers[step["key"]] = option
                st.session_state.onboarding_step += 1
            st.rerun()

    nav_left, nav_right = st.columns([1, 1])
    with nav_left:
        if st.session_state.onboarding_step > 0 and st.button("Back", use_container_width=True):
            st.session_state.onboarding_step -= 1
            st.rerun()
    with nav_right:
        can_continue = bool(answers.get(step["key"]))
        if st.button("Next", disabled=not can_continue, type="primary", use_container_width=True):
            st.session_state.onboarding_step += 1
            st.rerun()


def _render_starter_habit_step():
    answers = st.session_state.onboarding_answers
    focus_areas = answers.get("focus_areas") or ["Health and energy", "Productivity"]
    starter_choices = []
    for area in focus_areas:
        starter_choices.extend(STARTER_HABITS.get(area, []))

    selected = set(answers.get("selected_starters", []))
    st.markdown("## Pick your starting habits")
    st.caption("Choose the habits that feel easy enough to begin today.")

    for name, _, category in starter_choices:
        is_selected = name in selected
        emoji_map = {
            "health": "❤️", "lifestyle": "🏡", "finance": "💰",
            "learning": "📚", "productivity": "⏱️", "mindfulness": "🧘", "creativity": "🎨"
        }
        emoji = emoji_map.get(category, "✅")
        label = f"{'✓ ' if is_selected else ''}{emoji} {name}"
        if st.button(label, key=f"starter_{name}", use_container_width=True):
            if is_selected:
                selected.remove(name)
            else:
                selected.add(name)
            answers["selected_starters"] = list(selected)
            st.rerun()

    nav_left, nav_right = st.columns([1, 1])
    with nav_left:
        if st.button("Back", use_container_width=True):
            st.session_state.onboarding_step -= 1
            st.rerun()
    with nav_right:
        if st.button("Next", disabled=not selected, type="primary", use_container_width=True):
            st.session_state.onboarding_step += 1
            st.rerun()


def _render_companion_name_step(user: User):
    answers = st.session_state.onboarding_answers

    st.markdown("## Name your companion")
    st.caption("This character will stay on the page, react to check-ins, and grow with your routine.")
    companion_name = st.text_input(
        "Companion name",
        value=answers.get("companion_name", user.pet_name or "Buddy"),
        label_visibility="collapsed",
    )
    answers["companion_name"] = companion_name.strip() or "Buddy"

    nav_left, nav_right = st.columns([1, 1])
    with nav_left:
        if st.button("Back", use_container_width=True):
            st.session_state.onboarding_step -= 1
            st.rerun()
    with nav_right:
        if st.button("Start my dashboard", type="primary", use_container_width=True):
            _complete_onboarding(user)


def _complete_onboarding(user: User):
    answers = st.session_state.onboarding_answers
    focus_areas = answers.get("focus_areas") or ["Health and energy", "Productivity"]
    selected_starters = set(answers.get("selected_starters", []))

    apply_onboarding_profile(user, answers)
    for area in focus_areas:
        for name, habit_type, category in STARTER_HABITS.get(area, []):
            if name in selected_starters:
                _, error = add_habit(st.session_state.habits, name, habit_type, category)
                if error is None:
                    user.habits_created += 1

    user.add_xp(25)
    user.update_parameters(st.session_state.habits)
    save_data()
    save_user_data()
    del st.session_state.onboarding_step
    del st.session_state.onboarding_answers
    st.success("Setup complete. Your dashboard is ready.")
    st.rerun()


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: TODAY (Main Dashboard)
# ═══════════════════════════════════════════════════════════════════════════

def page_today(habits, user: User):
    """The main dashboard with game-like features."""
    # ── User Status Bar ──
    render_user_status_bar(user)
    
    st.markdown(f"# {t('dashboard.title')}")
    
    # ── Quick Stats ──
    render_stats_cards(habits)
    
    # ── XP & Level Progress ──
    render_xp_progress(user)
    
    # ── Character Stats + Monthly Activity ──
    stats_col, calendar_col = st.columns([4, 6])
    with stats_col:
        render_user_parameters(user, habits)
    with calendar_col:
        glass_card_start(t("dashboard.monthly_activity_title"), t("dashboard.monthly_activity_subtitle"))
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
    st.markdown(f"### {t('dashboard.today_tasks')}")
    
    if not habits:
        render_empty_state(
            message=t("dashboard.no_habits"),
            icon="🌟"
        )
    
    # ── Pro Tips Section ──
    with st.expander("💡 Professional Habit Tips", expanded=False):
        tips = [
            "**Habit Stacking**: Attach a new habit to an existing one (e.g., 'After I pour my coffee, I will meditate').",
            "**Start Small**: Making it too easy to fail is the key to consistency.",
            "**Never Miss Twice**: If you miss a day, make sure you don't miss the next one.",
            "**Environment Design**: Make the cues for your good habits obvious and the cues for bad habits invisible."
        ]
        import random
        st.info(random.choice(tips))

    habits_sorted = list(habits)
    for idx, h in enumerate(habits_sorted):
        key = f"{idx}_{h.name}"
        completed = h.is_completed_today()
        streak = h.get_current_streak()
        
        col1, col2, col3 = st.columns([6, 2, 2])
        
        with col1:
            status_icon = "✅" if completed else "⬜"
            st.markdown(f"**{status_icon} {h.emoji} {h.name}**")
            if streak > 0:
                st.caption(f"🔥 {t('dashboard.streak', days=streak)}")
        
        with col2:
            if not completed:
                if st.button(t("dashboard.checkin_button"), key=f"check_{key}", use_container_width=True, type="primary"):
                    h.mark_complete()
                    # Award XP
                    xp_earned = XP_HABIT_COMPLETION
                    if streak > 0:
                        xp_earned += XP_STREAK_BONUS
                    user.add_xp(xp_earned)
                    user.total_completions += 1
                    user.update_parameters(habits_sorted)
                    
                    # Check achievements
                    new_achievements = check_achievements(user, habits_sorted)
                    
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
            if st.button(t("dashboard.details_button"), key=f"detail_{key}", use_container_width=True):
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
                <div style="display: flex; justify-content: space-between; align-items: center; gap: 20px;">
                    <div>
                        <div style="font-size: 14px; font-weight: 700; color: {rank_info['color']};">
                            {user.title} • Level {user.level}
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 12px; color: var(--text2);">
                            {user.xp} XP
                        </div>
                    </div>
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


def render_user_parameters(user: User, habits: list = None):
    """Render user parameter stats as a hexagonal radar chart with category progress."""
    glass_card_start(t("profile.stats_title"), user.personality_type)

    params = [
        (t("profile.param_discipline"), user.discipline),
        (t("profile.param_consistency"), user.consistency),
        (t("profile.param_dedication"), user.dedication),
        (t("profile.param_focus"), user.focus),
        (t("profile.param_creativity"), user.creativity),
        (t("profile.param_resilience"), user.resilience),
    ]
    if st_echarts:
        options = {
            "radar": {
                "indicator": [{"name": name, "max": 100} for name, _ in params],
                "shape": "polygon",
                "splitNumber": 4,
                "axisName": {"color": "#ffffff"},
                "splitLine": {"lineStyle": {"color": "rgba(0,255,255,0.22)"}},
                "splitArea": {"areaStyle": {"color": ["rgba(0,255,255,0.03)", "rgba(255,0,255,0.03)"]}},
                "axisLine": {"lineStyle": {"color": "rgba(0,255,255,0.35)"}},
            },
            "series": [{
                "type": "radar",
                "data": [{
                    "value": [value for _, value in params],
                    "name": "Traits",
                    "areaStyle": {"color": "rgba(255,0,255,0.22)"},
                    "lineStyle": {"color": "#ff00ff", "width": 2},
                    "itemStyle": {"color": "#00ffff"},
                }],
            }],
        }
        st_echarts(options=options, height="320px")
    else:
        st.warning("Install streamlit-echarts to see the hex chart.")

    for name, value in params:
        color = "#10B981" if value >= 70 else "#F5A623" if value >= 40 else "#EF4444"
        st.markdown(f'''
        <div style="margin-bottom: 10px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                <span style="font-size: 14px; font-weight: 600; color: var(--text);">{name}</span>
                <span style="font-size: 14px; font-weight: 700; color: {color};">{value}</span>
            </div>
        </div>
        ''', unsafe_allow_html=True)

    if habits:
        st.markdown("<hr style='border-color: var(--border2); margin: 15px 0;'>", unsafe_allow_html=True)
        st.markdown(f"#### 📊 Category Breakdown")
        
        categories_habits = {cat: [] for cat in CATEGORIES}
        for h in habits:
            cat = getattr(h, "category", "lifestyle")
            if cat not in categories_habits:
                categories_habits[cat] = []
            categories_habits[cat].append(h)
            
        for cat, cat_habits in categories_habits.items():
            if not cat_habits:
                continue
                
            completed_today = sum(1 for h in cat_habits if h.is_completed_today())
            total = len(cat_habits)
            avg_rate = sum(h.get_completion_rate(30) for h in cat_habits) / total
            
            st.markdown(f"""
            <div style="
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: var(--radius-md);
                padding: 10px 14px;
                margin-bottom: 8px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            ">
                <div>
                    <span style="font-size: 14px; font-weight: 600; color: var(--text);">{CATEGORIES.get(cat, cat.title())}</span>
                </div>
                <div style="text-align: right; font-size: 13px; color: var(--text2);">
                    <span style="font-weight: 700; color: var(--accent2);">{avg_rate:.0f}% rate</span>
                    <span style="margin: 0 4px;">•</span>
                    <span>{completed_today}/{total} done</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    glass_card_end()


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: MY HABITS (Management)
# ═══════════════════════════════════════════════════════════════════════════

def page_manage(habits, user: User):
    """Habit management page."""
    st.markdown(f"# {t('habits.title')}")
    st.caption(t("habits.subtitle"))
    
    # ── Create New Habit Form ──
    with st.expander(t("habits.create_expander"), expanded=True):
        c1, c2, c3 = st.columns([4, 2, 2])
        
        with c1:
            name = st.text_input(t("habits.name_label"), 
                                placeholder=t("habits.name_placeholder"),
                                key="habit_name_input")
            
            # Simple reactive auto-suggest
            if "guessed_category" not in st.session_state:
                st.session_state.guessed_category = "lifestyle"
            if "prev_name" not in st.session_state:
                st.session_state.prev_name = ""
            
            if name and name != st.session_state.prev_name:
                st.session_state.guessed_category = guess_category(name)
                st.session_state.prev_name = name
        
        with c2:
            habit_type = st.selectbox(t("habits.type_label"), ["adopt", "quit"], 
                                     help=t("habits.type_help"))
        
        with c3:
            category_options = list(CATEGORIES.keys())
            try:
                category_index = category_options.index(st.session_state.guessed_category)
            except ValueError:
                category_index = 0
                
            category = st.selectbox(
                "Category",
                options=category_options,
                format_func=lambda x: CATEGORIES.get(x, x),
                index=category_index,
                key="habit_category_select"
            )
            # Sync back in case user changes it manually
            st.session_state.guessed_category = category
        
        if st.button(t("habits.create_button"), type="primary", use_container_width=True):
            if not name or not name.strip():
                st.error(t("habits.name_required"))
            else:
                result, error = add_habit(habits, name.strip(), habit_type, category)
                if error:
                    st.error(error)
                else:
                    user.habits_created += 1
                    user.add_xp(25)  # Bonus XP for creating a habit
                    check_achievements(user, habits)
                    st.success(f"🎉 {t('habits.created_success', name=name.strip())}")
                    save_data()
                    save_user_data()
                    st.rerun()
    
    # ── Active Habits List ──
    st.markdown(f"### {t('habits.active_title')}")
    
    if not habits:
        st.info(t("habits.none_yet"))
    else:
        # Data Export Feature
        import pandas as pd
        import io
        
        export_data = []
        for h in habits:
            export_data.append({
                "Name": h.name,
                "Type": h.habit_type,
                "Category": CATEGORIES.get(h.category, h.category),
                "Total Completions": h.get_total_completions(),
                "Current Streak": h.get_current_streak(),
                "Longest Streak": h.get_longest_streak(),
                "30-Day Rate (%)": h.get_completion_rate(30)
            })
        
        if export_data:
            df = pd.DataFrame(export_data)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Export Habit Data (CSV)",
                data=csv,
                file_name=f"habit_space_export_{date.today()}.csv",
                mime="text/csv",
                use_container_width=True
            )
            st.divider()

        for idx, h in enumerate(habits):
            rank = h.get_rank()
            streak = h.get_current_streak()
            
            c1, c2 = st.columns([8, 2])
            
            with c1:
                st.markdown(f"**{h.emoji} {h.name}**")
                streak_label = f"{t('dashboard.streak', days=streak)}"
                st.markdown(
                    f'<div style="font-size: 14px; color: var(--text2); margin-top: 2px;">'
                    f'{rank_badge(rank, text_only=True)} • {streak_label}'
                    f'</div>',
                    unsafe_allow_html=True
                )
            
            with c2:
                if st.button(t("habits.remove_button"), key=f"del_{idx}_{h.name}", type="secondary"):
                    delete_habit(habits, h.name)
                    db_delete_habit(user.username, h.name)
                    st.success(t("habits.removed_success", name=h.name))
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
    st.markdown(f"# {t('events.title')}")
    st.caption(t('events.subtitle'))

    events = load_events()

    # ── Active Events ──
    st.markdown(f"### {t('events.active_title')}")

    active_events = [e for e in events if e.is_active]

    if not active_events:
        st.info(t('events.none_active'))
    else:
        for event in active_events:
            is_joined = event.id in user.joined_events
            is_completed = event.id in user.completed_events
            
            glass_card_start(f"{event.emoji} {event.name}")
            
            st.markdown(f"**{event.description}**")
            st.caption(f"📅 {event.start_date} to {event.end_date}")
            st.caption(f"🏆 {t('events.reward', xp=event.xp_reward)}")
            st.caption(f"📝 {t('events.suggested', habit=event.habit_suggestion)}")
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                if is_completed:
                    st.success(t('events.completed_reward'))
                elif is_joined:
                    st.info(t('events.in_progress'))
            
            with col2:
                if not is_joined and not is_completed:
                    if st.button(t('events.join_button'), key=f"join_{event.id}", 
                                type="primary", use_container_width=True):
                        user.joined_events.append(event.id)
                        user.events_joined += 1
                        user.add_xp(25)  # Bonus for joining
                        check_achievements(user)
                        update_user(user)
                        save_events(events)
                        st.success(t('events.joined_success'))
                        st.rerun()
            
            glass_card_end()
    
    # ── Completed Events ──
    if user.completed_events:
        st.markdown(f"### {t('events.completed_title')}")
        for event in events:
            if event.id in user.completed_events:
                st.markdown(f"✅ **{event.name}** - {event.xp_reward} XP earned")


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: RANKINGS (Leaderboard)
# ═══════════════════════════════════════════════════════════════════════════

def page_rankings(user: User):
    """Global rankings/leaderboard page."""
    # ── Handle Profile View ──
    if st.session_state.get("view_profile"):
        target_username = st.session_state.get("view_profile")
        render_user_profile_view(target_username)
        return

    st.markdown(f"# 🏆 {t('rankings.title')}")
    st.caption(t('rankings.subtitle'))
    
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
    ">
        <div style="text-align: center; margin-bottom: 16px;">
            <div style="font-size: 48px; margin-bottom: 8px;">{rank_info['icon']}</div>
            <div style="font-size: 14px; color: var(--text2);">Your Global Rank</div>
            <div style="font-size: 36px; font-weight: 700; color: {rank_info['color']};">
                #{user_position if user_position > 0 else '—'}
            </div>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 12px;">
            <div>
                <div style="font-size: 14px; color: var(--text2);">
                    {user.title} • Level {user.level}
                </div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 18px; font-weight: 700; color: var(--accent2);">
                    {user.xp} XP
                </div>
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    # ── Leaderboard ──
    rankings = get_global_rankings(15)
    
    glass_card_start("Top Players")
    st.caption("Click any player to view their profile")

    # Hidden trigger for selection
    st.markdown('<div class="pet-trigger-hidden">', unsafe_allow_html=True)
    selected_user = st.text_input("Selection helper", key="rank_select_trigger")
    if selected_user:
        st.session_state.view_profile = selected_user
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
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
        
        username_display = player.username.strip()
        st.markdown(f'''<div onclick="const ins=window.parent.document.querySelectorAll('input');for(const i of ins){{if(i.getAttribute('aria-label')==='Selection helper'){{i.value='{username_display}';i.dispatchEvent(new Event('input',{{bubbles:true}}));i.dispatchEvent(new Event('change',{{bubbles:true}}));break;}}}}" style="display:flex;align-items:center;gap:12px;padding:12px 16px;border-radius:var(--radius-lg);margin-bottom:8px;{bg_style}border:1px solid {'var(--accent2)' if is_current_user else 'var(--border2)'};cursor:pointer;transition:transform 0.2s ease;" onmouseover="this.style.transform='translateX(4px)'" onmouseout="this.style.transform='translateX(0)'"><div style="font-size:20px;font-weight:700;color:var(--text);width:30px;">{'🥇' if rank_num==1 else '🥈' if rank_num==2 else '🥉' if rank_num==3 else f'#{rank_num}'}</div><div style="font-size:24px;">{player_rank['icon']}</div><div style="flex:1;"><div style="font-weight:600;color:var(--text);margin-bottom:4px;">{username_display}{' (You)' if is_current_user else ''}</div><div style="display:flex;justify-content:space-between;align-items:center;"><div><div style="font-size:12px;color:var(--text2);">{player.title} • Level {player.level}</div></div><div style="text-align:right;"><div style="font-size:16px;font-weight:700;color:var(--accent2);">{player.xp} XP</div></div></div></div></div>''', unsafe_allow_html=True)
    
    glass_card_end()
    
    # ── Total Players ──
    total_players = len(get_global_rankings(9999))
    st.caption(f"Total players: {total_players}")


def render_user_profile_view(username: str):
    """Detailed profile view for a specific user."""
    from src.auth import get_user_by_username
    from src.storage import load_habits
    from src.habits import Habit

    target_user = get_user_by_username(username)
    if not target_user:
        st.error("User not found.")
        if st.button("← Back to Rankings"):
            st.session_state.view_profile = None
            st.rerun()
        return

    col_back, col_title = st.columns([1, 4])
    with col_back:
        if st.button("← Back", use_container_width=True):
            st.session_state.view_profile = None
            st.rerun()
    
    rank_info = target_user.get_rank_info()
    
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: var(--space-xl);">
        <div style="font-size: 64px; margin-bottom: 8px;">{rank_info['icon']}</div>
        <h1 style="margin: 0;">{target_user.username}</h1>
        <div style="color: {rank_info['color']}; font-weight: 700; font-size: 18px;">
            {target_user.title} • Level {target_user.level}
        </div>
        <div style="color: var(--text2); font-size: 14px; margin-top: 4px;">
            Building habits since {target_user.created_at}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Traits ──
    glass_card_start("Character Stats")
    params = [
        ("Discipline", target_user.discipline),
        ("Consistency", target_user.consistency),
        ("Dedication", target_user.dedication),
        ("Focus", target_user.focus),
        ("Creativity", target_user.creativity),
        ("Resilience", target_user.resilience),
    ]
    
    cols = st.columns(3)
    for i, (name, value) in enumerate(params):
        color = "#10B981" if value >= 70 else "#F5A623" if value >= 40 else "#EF4444"
        with cols[i % 3]:
            st.markdown(f'''
            <div style="text-align: center; margin-bottom: 16px;">
                <div style="font-size: 12px; color: var(--text2);">{name}</div>
                <div style="font-size: 24px; font-weight: 700; color: {color};">{value}</div>
            </div>
            ''', unsafe_allow_html=True)
    glass_card_end()

    # ── Top 3 Habits ──
    st.markdown("### 🏆 Top 3 Consistent Habits")
    raw_habits = load_habits(username)
    habits = [Habit.from_dict(h) for h in raw_habits]
    
    # Sort by completion rate (30 days) and then streak
    sorted_habits = sorted(habits, key=lambda h: (h.get_completion_rate(30), h.get_current_streak()), reverse=True)
    top_3 = sorted_habits[:3]

    if not top_3:
        st.info(f"{username} hasn't started any habits yet.")
    else:
        for h in top_3:
            h_rank = h.get_rank()
            rate = h.get_completion_rate(30)
            streak = h.get_current_streak()
            
            st.markdown(f'''
            <div style="
                background: var(--glass);
                border: 1px solid {h_rank['color']}44;
                border-left: 4px solid {h_rank['color']};
                border-radius: var(--radius-md);
                padding: 16px;
                margin-bottom: 12px;
                display: flex;
                align-items: center;
                gap: 16px;
            ">
                <div style="font-size: 32px;">{h.emoji}</div>
                <div style="flex: 1;">
                    <div style="font-weight: 700; color: var(--text);">{h.name}</div>
                    <div style="font-size: 12px; color: var(--text2);">{h.habit_type.title()}ing</div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 14px; font-weight: 700; color: var(--accent2);">{rate}% Consistent</div>
                    <div style="font-size: 12px; color: var(--text2);">{streak} day streak</div>
                </div>
            </div>
            ''', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: ACHIEVEMENTS
# ═══════════════════════════════════════════════════════════════════════════

def page_achievements(user: User):
    """Achievements page."""
    st.markdown(f"# {t('achievements.title')}")
    st.caption(t('achievements.subtitle'))
    
    # Check for new achievements
    new_achievements = check_achievements(user, st.session_state.habits)
    if new_achievements:
        for ach_id in new_achievements:
            ach = ACHIEVEMENTS[ach_id]
            st.success(t('achievements.new', icon=ach['icon'], name=ach['name']))
        save_user_data()
    
    # ── Earned Achievements ──
    st.markdown(f"### {t('achievements.earned_title')}")
    
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


def render_profile_page(user: User, habits: list):
    """Unified Profile & Settings page with account + app controls."""
    st.markdown("## " + t("nav.profile"))

    if not user:
        st.info(t("profile.login_to_edit"))
        return

    left_col, right_col = st.columns([1, 1])

    with left_col:
        # ── ACCOUNT INFO ──
        st.markdown("### " + t("profile.account_title"))
        with st.form("account_form", clear_on_submit=False):
            current_username = st.text_input(t("profile.username"), value=user.username)
            new_password = st.text_input(t("profile.new_password"), type="password", placeholder="Leave blank to keep current")
            confirm_password = st.text_input(t("profile.confirm_password"), type="password")
            submitted = st.form_submit_button(t("profile.save"))
            if submitted:
                if not current_username or not current_username.strip():
                    st.error(t("profile.username_empty"))
                elif new_password:
                    if new_password != confirm_password:
                        st.error(t("profile.passwords_do_not_match"))
                    elif len(new_password) < 4:
                        st.error(t("profile.password_too_short"))
                    else:
                        existing = get_user_by_username(current_username)
                        if existing and existing.username.lower() != user.username.lower():
                            st.error(t("profile.username_taken"))
                        else:
                            user.username = current_username.strip().lower()
                            user.password_hash = hashlib.sha256(new_password.encode()).hexdigest()
                            save_user_data()
                            st.success(t("profile.saved"))
                else:
                    if current_username.strip().lower() != user.username:
                        existing = get_user_by_username(current_username)
                        if existing and existing.username.lower() != user.username.lower():
                            st.error(t("profile.username_taken"))
                        else:
                            user.username = current_username.strip().lower()
                            update_user(user)
                            save_user_data()
                            st.success(t("profile.saved"))
        with left_col:
            # ── PET / COMPANION ──
            with st.form("pet_form", clear_on_submit=False):
                from src.pet_types import PET_TYPES
                current_pet_code = (st.session_state.get("pet_type") or getattr(user, "personality_type", None) or "fox")
                current_pet_code = current_pet_code if current_pet_code in PET_TYPES else "fox"
                pet_name = st.text_input(t("profile.companion_name"), value=user.pet_name or t("profile.companion_default"))
                mood = st.selectbox(
                    t("profile.companion_mood"),
                    [t("profile.mood_curious"), t("profile.mood_energized"), t("profile.mood_sleepy"), t("profile.mood_loyal")],
                    index=0,
                )
                pet_type = st.selectbox(
                    "Pet type",
                    list(PET_TYPES.keys()),
                    index=list(PET_TYPES.keys()).index(current_pet_code),
                    format_func=lambda code: PET_TYPES[code].label,
                )
                if st.form_submit_button(t("profile.save_companion")):
                    user.pet_name = pet_name.strip() or t("profile.companion_default")
                    user.pet_mood = mood
                    st.session_state.pet_type = pet_type
                    save_user_data()
                    from src.companion_widget import speak
                    speak(f"{PET_TYPES[pet_type].emoji} {user.pet_name} reconnected")
                    st.success(t("profile.companion_updated"))

            if st.button("← Back to dashboard", use_container_width=True):
                st.session_state.active_page = "Today"
                st.rerun()

    with right_col:
        # ── APPEARANCE ──
        st.markdown("### " + t("profile.appearance_title"))
        theme = st.session_state.get("theme", "Dark")
        theme = st.radio("Theme", ["Dark", "Light", "Retro"], index=["Dark", "Light", "Retro"].index(theme))
        st.session_state.theme = theme

        from src.i18n import SUPPORTED_LANGUAGES, LANGUAGE_OPTIONS, set_active_language
        current_lang = st.session_state.get("app_language", "en")
        lang_options = [f"{code}: {LANGUAGE_OPTIONS.get(code, code)}" for code in SUPPORTED_LANGUAGES]
        current_index = SUPPORTED_LANGUAGES.index(current_lang) if current_lang in SUPPORTED_LANGUAGES else 0
        new_lang_value = st.selectbox(
            "Language",
            options=SUPPORTED_LANGUAGES,
            format_func=lambda code: LANGUAGE_OPTIONS.get(code, code),
            index=current_index,
        )
        if new_lang_value != current_lang:
            set_active_language(new_lang_value)
            st.rerun()

        # ─- ACTIONS ──
        st.markdown("### Account")
        if st.button("Logout", type="secondary"):
            for key in ["current_user", "habits", "active_page", "selected_habit", "oauth_checked", "onboarding_step", "onboarding_answers"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════════════════

def main():
    """Main application entry point."""
    init_app()
    apply_design()
    handle_google_oauth_callback()
    
    # Check if user is logged in
    if st.session_state.current_user is None:
        page_login()
        return
    
    user = st.session_state.current_user
    habits = st.session_state.habits
    active = st.session_state.active_page

    if not user.onboarding_completed:
        page_onboarding(user)
        return

    # ── Render Navigation ──
    render_top_nav(habits, active, st.session_state.theme)
    render_companion()

    # Apply today's interactions to the pet/session state.
    
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
        elif active == "Profile":
            render_profile_page(user, habits)
        else:
            st.error("Page not found.")

if __name__ == "__main__":
    main()
