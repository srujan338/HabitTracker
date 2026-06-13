"""
=============================================================================
UI COMPONENTS MODULE - Visual Building Blocks
=============================================================================
This module provides reusable UI components that create a modern, addictive
user experience. Each function is designed to be:
- Visually appealing with smooth animations
- Accessible and user-friendly
- Consistent with the overall design system

Components included:
- Navigation bar with theme toggle
- Glass cards for content containment
- Rank/achievement badges with glow effects
- Progress indicators and streak displays
- Celebration animations for completions
=============================================================================
"""

import streamlit as st
from datetime import date
from src.i18n import t, render_language_selector, set_active_language, DEFAULT_LANGUAGE


def get_streak_flame_emoji(streak: int) -> str:
    """
    Returns a flame emoji that intensifies based on streak length.
    
    This creates a visual reward system where longer streaks have
    more impressive flame indicators, encouraging continued use.
    
    Args:
        streak: Current streak count (number of consecutive days)
    
    Returns:
        Appropriate flame emoji for the streak level
    """
    if streak >= 30:
        return "🔥"  # Legendary flame
    elif streak >= 14:
        return "🔥"  # Strong flame
    elif streak >= 7:
        return "⚡"  # Lightning (energetic)
    elif streak >= 3:
        return "✨"  # Sparkle
    elif streak >= 1:
        return "💪"  # Flex
    else:
        return "🌱"  # Seed (not started)


def get_streak_intensity(streak: int) -> float:
    """
    Calculates visual intensity (0.0 to 1.0) for streak display.
    
    Used for CSS animations and visual effects intensity.
    """
    return min(streak / 30.0, 1.0)


def glass_card_start(title: str = None, subtitle: str = None):
    """
    Opens a frosted glass card container.
    
    This creates the signature "glass morphism" effect that gives
    the app its modern, premium feel. The card has:
    - Semi-transparent background with blur
    - Subtle border and shadow
    - Smooth hover animations
    
    Args:
        title: Optional card title displayed prominently
        subtitle: Optional subtitle for additional context
    """
    title_html = ""
    if title:
        title_html += f'<h2 style="margin:0 0 4px 0; font-size:24px; font-weight:700; color:var(--text);">{title}</h2>'
    if subtitle:
        title_html += f'<p style="margin:0 0 16px 0; font-size:14px; color:var(--text2);">{subtitle}</p>'
    
    if title_html:
        st.markdown(
            f'<div class="glass-card slide-in">{title_html}',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="glass-card slide-in">',
            unsafe_allow_html=True
        )


def glass_card_end():
    """
    Closes the glass card container.
    
    Must be called after glass_card_start() to properly close the div.
    """
    st.markdown('</div>', unsafe_allow_html=True)


def rank_badge(rank: dict, text_only: bool = False, show_glow: bool = True) -> str:
    """
    Creates a styled achievement/rank badge.
    
    Badges provide visual recognition for user achievements and
    streak milestones. They feature:
    - Color-coded ranks (Bronze → Silver → Gold → Legend)
    - Optional glow animation for emphasis
    - Icon + label combination
    
    Args:
        rank: Dictionary containing label, color, bg, and icon
        text_only: If True, returns plain text without badge styling
        show_glow: If True, adds animated glow effect
    
    Returns:
        HTML string for the badge
    """
    color = rank.get("color", "#94A3B8")
    icon = rank.get("icon", "—")
    label = rank.get("label", "Unknown")
    bg = rank.get("bg", "rgba(148,163,184,0.08)")
    
    if text_only:
        return f'<span style="color:{color}; font-weight:700;">{icon} {label}</span>'
    
    glow_effect = ""
    if show_glow:
        glow_effect = f'box-shadow: 0 0 12px {color}44;'
    
    return (
        f'<span class="achievement-badge" style="color:{color}; '
        f'background:{bg}; border:1px solid {color}44; {glow_effect}">'
        f'{icon} {label}</span>'
    )


def progress_ring(percentage: float, size: int = 60, stroke: int = 6, color: str = None):
    """
    Creates an SVG circular progress indicator.
    
    Progress rings provide an at-a-glance view of completion status.
    They're more visually engaging than linear progress bars and
    work well for habit completion percentages.
    
    Args:
        percentage: Completion percentage (0-100)
        size: Diameter in pixels
        stroke: Line thickness in pixels
        color: Custom color (defaults to accent color)
    
    Returns:
        SVG HTML string for the progress ring
    """
    if color is None:
        color = "var(--accent2)"
    
    radius = (size - stroke) / 2
    circumference = 2 * 3.14159 * radius
    offset = circumference - (percentage / 100) * circumference
    
    # Determine color based on completion level
    if percentage >= 80:
        stroke_color = "#10B981"  # Green for high completion
    elif percentage >= 50:
        stroke_color = "#F5A623"  # Orange for medium
    else:
        stroke_color = "#EF4444"  # Red for low
    
    return f'''
    <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" style="transform: rotate(-90deg);">
        <!-- Background circle -->
        <circle cx="{size/2}" cy="{size/2}" r="{radius}" 
                fill="none" stroke="rgba(128,128,128,0.2)" stroke-width="{stroke}" />
        <!-- Progress circle -->
        <circle cx="{size/2}" cy="{size/2}" r="{radius}" 
                fill="none" stroke="{stroke_color}" stroke-width="{stroke}"
                stroke-dasharray="{circumference} {circumference}"
                stroke-dashoffset="{offset}"
                stroke-linecap="round"
                style="transition: stroke-dashoffset 0.8s cubic-bezier(0.4, 0, 0.2, 1);" />
        <!-- Percentage text -->
        <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" 
              fill="var(--text)" font-size="{size * 0.3}px" font-weight="700"
              style="transform: rotate(90deg); transform-origin: center;">
            {int(percentage)}%
        </text>
    </svg>
    '''


def streak_display(streak: int, longest: int) -> str:
    """
    Creates a comprehensive streak display with flame animation.
    
    Shows current streak with animated flame that pulses faster
    for longer streaks, creating a sense of urgency and achievement.
    
    Args:
        streak: Current consecutive day count
        longest: Best streak ever achieved
    
    Returns:
        HTML string with streak display
    """
    flame = get_streak_flame_emoji(streak)
    intensity = get_streak_intensity(streak)
    
    # Animation speed increases with streak length
    anim_duration = max(1.5 - (intensity * 0.8), 0.5)
    
    html = f'''
    <div style="display: flex; align-items: center; gap: 8px;">
        <span class="streak-flame" style="font-size: 24px; animation-duration: {anim_duration}s;">{flame}</span>
        <div>
            <div style="font-size: 20px; font-weight: 700; color: var(--text);">
                {streak} <span style="font-size: 12px; color: var(--text2); font-weight: 400;">days</span>
            </div>
            <div style="font-size: 11px; color: var(--text2);">
                Best: {longest} days
            </div>
        </div>
    </div>
    '''
    return html


def habit_card(habit, show_check: bool = True) -> str:
    """
    Creates a complete habit card with all information.
    
    Each card displays:
    - Habit name and emoji
    - Current streak with flame
    - Completion status
    - Quick action buttons
    
    Args:
        habit: Habit object with all data
        show_check: Whether to show completion checkbox
    
    Returns:
        HTML string for the habit card
    """
    completed = habit.is_completed_today()
    streak = habit.get_current_streak()
    rank = habit.get_rank()
    
    # Card styling based on completion status
    card_class = "habit-card completed" if completed else "habit-card"
    checkmark = "✅" if completed else "⬜"
    
    html = f'''
    <div class="{card_class} fade-in">
        <div style="font-size: 28px;">{habit.emoji}</div>
        <div style="flex: 1;">
            <div style="font-weight: 600; color: var(--text); font-size: 16px;">
                {habit.name}
            </div>
            <div style="font-size: 12px; color: var(--text2); margin-top: 2px;">
                {rank_badge(rank, text_only=True)}
            </div>
        </div>
        <div style="text-align: center;">
            <div style="font-size: 14px; color: var(--text2);">Streak</div>
            <div style="font-size: 18px; font-weight: 700; color: var(--text);">
                {streak}🔥
            </div>
        </div>
    </div>
    '''
    return html


def celebration_effect(habit_name: str):
    """
    Triggers a celebration animation when a habit is completed.
    
    This creates a satisfying visual reward that makes completing
    habits feel rewarding and encourages continued use.
    
    Args:
        habit_name: Name of the completed habit for the message
    """
    st.markdown(f'''
    <div class="celebration-overlay" style="
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 9999;
        display: flex;
        align-items: center;
        justify-content: center;
        animation: fadeInOut 2s ease-in-out;
    ">
        <div style="
            background: var(--glass-heavy);
            backdrop-filter: blur(20px);
            padding: 24px 48px;
            border-radius: 20px;
            border: 1px solid var(--border2);
            text-align: center;
            animation: celebrate 0.6s ease-in-out;
        ">
            <div style="font-size: 48px; margin-bottom: 8px;">🎉</div>
            <div style="font-size: 18px; font-weight: 700; color: var(--text);">
                Amazing! "{habit_name}" completed!
            </div>
            <div style="font-size: 14px; color: var(--text2); margin-top: 4px;">
                Keep the streak going! 🔥
            </div>
        </div>
    </div>
    
    <style>
    @keyframes fadeInOut {{
        0% {{ opacity: 0; }}
        20% {{ opacity: 1; }}
        80% {{ opacity: 1; }}
        100% {{ opacity: 0; }}
    }}
    </style>
    ''', unsafe_allow_html=True)


def motivation_message(streak: int, completion_rate: float) -> str:
    """
    Generates contextual motivational messages based on progress.
    
    Different messages for different situations:
    - New habits: Encouragement to build consistency
    - Growing streaks: Celebration and momentum building
    - High completion: Recognition of dedication
    - Struggling: Gentle encouragement
    
    Args:
        streak: Current streak count
        completion_rate: Overall completion percentage
    
    Returns:
        Motivational message string
    """
    messages = []
    
    # Streak-based messages
    if streak == 0:
        messages.append("🌱 Every journey starts with a single step. Today could be day 1!")
    elif streak == 1:
        messages.append("🎯 You've started! The hardest part is beginning.")
    elif streak == 3:
        messages.append("✨ 3 days! You're building real momentum now!")
    elif streak == 7:
        messages.append("🔥 One week strong! You're forming a real habit!")
    elif streak == 14:
        messages.append("💪 Two weeks! That's serious dedication!")
    elif streak == 30:
        messages.append("🏆 A full month! You're officially a habit master!")
    
    # Completion rate messages
    if completion_rate >= 90:
        messages.append("⭐ Incredible consistency! You're in the top 1%!")
    elif completion_rate >= 70:
        messages.append("👏 Great progress! You're building strong habits!")
    elif completion_rate >= 50:
        messages.append("💡 You're halfway there! Every check-in counts!")
    elif completion_rate > 0:
        messages.append("🌟 Every effort matters. Keep showing up!")
    
    if messages:
        return messages[0]  # Return first matching message
    return "🚀 You're doing great! Keep going!"


def render_top_nav(habits: list, active_page: str, theme: str):
    """
    Renders the main navigation bar.
    
    The nav bar includes:
    - App logo with branding
    - Page navigation buttons
    - Theme toggle (dark/light mode)
    - Active state highlighting
    
    Args:
        habits: List of all habits (for potential badge display)
        active_page: Currently active page name
        theme: Current theme setting ("Dark" or "Light")
    """
    # Create 4-column layout: Logo | Navigation | Language | Theme Toggle
    c1, c2, cl, c3 = st.columns([2, 6, 2, 1])
    
    # ── COLUMN 1: LOGO ──
    with c1:
        st.markdown(
            '<h1 style="font-size: 26px; margin:0; font-family:\'Space Grotesk\', sans-serif; '
            'font-weight: 700;">'
            'habit<span style="color:var(--accent2);">.</span>space</h1>', 
            unsafe_allow_html=True
        )

    # ── COLUMN 2: NAVIGATION BUTTONS ──
    with c2:
        pages = ["Today", "My Habits", "Events", "Rankings", "Achievements", "Profile"]
        page_keys = {
            "Today": "nav.home",
            "My Habits": "nav.habits",
            "Events": "nav.events",
            "Rankings": "nav.rankings",
            "Achievements": "nav.achievements",
            "Profile": "nav.profile"
        }
        icons = ["🏠", "📋", "🎯", "🏆", "🎖️", "👤"]
        nav_cols = st.columns(len(pages))
        
        for i, (p, icon) in enumerate(zip(pages, icons)):
            # Determine if this page is currently active
            is_active = (active_page == p) or (p == "Today" and active_page == "Habit Detail")
            
            # Translate label
            translated_label = t(page_keys[p])
            
            # Style active button differently
            label = f"{icon} **{translated_label}**" if is_active else f"{icon} {translated_label}"
            
            # Custom styling for active state
            if nav_cols[i].button(label, key=f"nav_{p}", use_container_width=True):
                st.session_state.active_page = p
                st.rerun()

    # ── COLUMN L: LANGUAGE SELECTOR ──
    with cl:
        render_language_selector()

    # ── COLUMN 3: THEME TOGGLE ──
    with c3:
        # Show appropriate icon for current theme
        themes = ["Dark", "Light", "Retro"]
        icons = ["🌙", "☀️", "🕹️"]
        
        current_idx = themes.index(theme)
        next_idx = (current_idx + 1) % len(themes)
        
        theme_icon = icons[current_idx]
        theme_label = themes[next_idx]
        
        if st.button(f"{theme_icon}", key="theme_toggle", 
                     help=f"Switch to {theme_label} theme"):
            st.session_state.theme = themes[next_idx]
            st.rerun()
    
    # Add subtle divider below nav
    st.divider()


def render_stats_cards(habits: list):
    """
    Renders the top-level statistics cards.
    
    Shows three key metrics:
    - Total habits being tracked
    - Habits completed today
    - Best current streak
    
    These provide quick motivation and progress overview.
    
    Args:
        habits: List of all habit objects
    """
    c1, c2, c3 = st.columns(3)
    
    # Calculate statistics
    total_habits = len(habits)
    completed_today = sum(1 for h in habits if h.is_completed_today())
    best_streak = max((h.get_current_streak() for h in habits), default=0)
    completion_rate = round((completed_today / total_habits * 100) if total_habits > 0 else 0)
    
    # Card 1: Total Habits
    with c1:
        st.metric(
            label="📊 Total Habits",
            value=total_habits,
            help="Number of habits you're currently tracking"
        )
    
    # Card 2: Completed Today with progress ring
    with c2:
        if total_habits > 0:
            st.metric(
                label="✅ Completed Today",
                value=f"{completed_today}/{total_habits}",
                delta=f"{completion_rate}%"
            )
        else:
            st.metric(
                label="✅ Completed Today",
                value="0/0",
                delta=None
            )
    
    # Card 3: Best Streak with flame
    with c3:
        flame = get_streak_flame_emoji(best_streak)
        st.metric(
            label=f"{flame} Best Streak",
            value=f"{best_streak} days",
            help="Your longest current streak across all habits"
        )


def render_empty_state(message: str = None, icon: str = "🌟"):
    """
    Renders an empty state when no data exists.
    
    Empty states should be friendly and guide users to action,
    not just show blank space.
    
    Args:
        message: Custom message to display
        icon: Emoji icon to show
    """
    if message is None:
        message = "No habits yet. Start your journey by creating your first habit!"
    
    st.markdown(f'''
    <div style="
        text-align: center;
        padding: 48px 24px;
        opacity: 0.7;
    ">
        <div style="font-size: 48px; margin-bottom: 16px;">{icon}</div>
        <div style="font-size: 16px; color: var(--text2); max-width: 400px; margin: 0 auto;">
            {message}
        </div>
    </div>
    ''', unsafe_allow_html=True)


def render_loading_spinner(text: str = "Loading..."):
    """
    Shows a loading indicator during data fetches.
    
    Args:
        text: Loading message to display
    """
    st.markdown(f'''
    <div style="
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 12px;
        padding: 24px;
        color: var(--text2);
    ">
        <div class="spinner"></div>
        <span>{text}</span>
    </div>
    ''', unsafe_allow_html=True)


def render_pet_companion(user_data: dict, habits: list):
    """Render a floating mythical pet companion from the pet state."""
    from src.pet_types import PET_TYPES, pet_type_for_code
    from src.pet_ai import load_state

    name = user_data.get("pet_name") or user_data.get("pet_mood") or "Companion"
    state = load_state(getattr(user_data, "username", None) or user_data.get("username", "default"))
    pet = pet_type_for_code(state.pet_type) if state and getattr(state, "pet_type", None) else None
    if not pet:
        pet = next(iter(PET_TYPES.values()))

    mood = "Happy"
    message = pet.greeting
    if habits:
        completed_today = sum(1 for h in habits if h.is_completed_today())
        total = len(habits)
        if completed_today == total and total:
            mood = "Excited"
        elif completed_today > 0:
            mood = "Curious"
            
        completed_cats = [getattr(h, "category", "lifestyle") for h in habits if h.is_completed_today()]
        if completed_cats:
            cat_counts = {}
            for c in completed_cats:
                cat_counts[c] = cat_counts.get(c, 0) + 1
            cat_summary = ", ".join([f"{count} {cat.title()}" for cat, count in cat_counts.items()])
            message = f"Today's wins: {cat_summary}. Thriving!"
    else:
        message = "No habits tracked yet. Let's start a new routine!"

    st.markdown(
        f"""
        <div class="arcane-pet" title="{name} - {pet.label}">
          <div class="arcane-pet-bubble">
            <strong>{name}</strong><br>
            {message}
          </div>
          <div class="arcane-pet-aura"></div>
          <div class="arcane-pet-body">
            <div class="arcane-pet-eye left"></div>
            <div class="arcane-pet-eye right"></div>
            <div class="arcane-pet-rune"></div>
          </div>
          <div class="arcane-pet-shadow"></div>
          <div class="arcane-pet-meta">{mood} • {pet.label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
