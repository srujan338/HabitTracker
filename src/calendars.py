"""
=============================================================================
CALENDAR RENDERING MODULE - Visual Progress Tracking
=============================================================================
This module transforms habit completion data into beautiful, interactive
calendar visualizations. The calendars serve as both:
- Progress tracking tools (see your consistency at a glance)
- Motivation engines (visual proof of your dedication)

Features:
- Global calendar: Overview of all habit activity
- Habit-specific calendar: Deep dive into single habit progress
- Color-coded days: Green for completed, red for missed
- Animated transitions and hover effects
- Current day highlighting

Design Philosophy:
"Show, don't tell" - Users should understand their progress
instantly without reading numbers.
=============================================================================
"""

import streamlit as st
import calendar
from datetime import date, timedelta
from src.habits import Habit


def get_day_status(this_date: date, habit_days: dict, created: date) -> dict:
    """
    Determines the visual status of a calendar day.
    
    Each day can be in one of several states:
    - Future: Not yet reachable, dimmed
    - Before created: Habit didn't exist, neutral
    - Completed: Habit was done, green
    - Missed: Habit exists but not done, red
    - Today: Current day, highlighted border
    
    Args:
        this_date: The date being evaluated
        habit_days: Dict of completed days for the habit
        created: Date when the habit was created
    
    Returns:
        Dictionary with background, border, text colors and status label
    """
    today = date.today()
    is_today = this_date == today
    is_future = this_date > today
    before_created = this_date < created
    
    # Default styles
    styles = {
        "bg": "transparent",
        "border": "0.5px solid var(--border2)",
        "text": "var(--text3)",
        "status": "neutral",
        "opacity": "1"
    }
    
    # Future days: barely visible
    if is_future:
        styles.update({
            "bg": "transparent",
            "border": "0.5px solid var(--border2)",
            "text": "var(--text3)",
            "opacity": "0.3",
            "status": "future"
        })
    
    # Before habit existed: neutral
    elif before_created:
        styles.update({
            "bg": "transparent",
            "border": "0.5px solid var(--border2)",
            "text": "var(--text3)",
            "opacity": "0.4",
            "status": "before_created"
        })
    
    # Completed: vibrant green with glow
    elif habit_days.get(this_date.day):
        styles.update({
            "bg": "rgba(16, 185, 129, 0.25)",
            "border": "1px solid rgba(16, 185, 129, 0.5)",
            "text": "#10B981",
            "status": "completed"
        })
    
    # Missed: subtle red
    else:
        styles.update({
            "bg": "rgba(239, 68, 68, 0.1)",
            "border": "0.5px solid rgba(239, 68, 68, 0.3)",
            "text": "rgba(239, 68, 68, 0.7)",
            "status": "missed"
        })
    
    # Today always gets special highlighting
    if is_today and not is_future:
        styles["border"] = "2px solid var(--accent2)"
        styles["status"] = "today"
    
    return styles


def render_calendar_cell(day_num: int, year: int, month: int, 
                         habit_days: dict, created: date, 
                         is_empty: bool = False) -> str:
    """
    Renders a single calendar day cell.
    
    Each cell is a small square that shows:
    - The day number
    - Color indicating completion status
    - Hover effects for interactivity
    
    Args:
        day_num: Day of month (1-31)
        year: Full year
        month: Month number (1-12)
        habit_days: Dict of completed days
        created: Habit creation date
        is_empty: If True, renders empty spacer cell
    
    Returns:
        HTML string for the cell
    """
    if is_empty or day_num == 0:
        return '<div></div>'
    
    this_date = date(year, month, day_num)
    styles = get_day_status(this_date, habit_days, created)
    
    # Build CSS classes for styling
    css_classes = ["calendar-cell"]
    if styles["status"] == "today":
        css_classes.append("today")
    elif styles["status"] == "completed":
        css_classes.append("completed")
    elif styles["status"] == "missed":
        css_classes.append("missed")
    
    # Add tooltip for context
    tooltip = ""
    if styles["status"] == "today":
        tooltip = "Today"
    elif styles["status"] == "completed":
        tooltip = "Completed ✓"
    elif styles["status"] == "missed":
        tooltip = "Missed ✗"
    elif styles["status"] == "future":
        tooltip = "Future"
    
    cell_html = (
        f'<div class="{" ".join(css_classes)}" '
        f'style="background:{styles["bg"]};border:{styles["border"]};'
        f'color:{styles["text"]};opacity:{styles["opacity"]};'
        f'" data-tooltip="{tooltip}" title="{tooltip}">'
        f'{day_num}</div>'
    )
    
    return cell_html


def render_global_calendar(habits: list):
    """
    Shows combined activity across ALL habits in a monthly grid.
    
    This "heatmap" style view lets users see their overall consistency
    at a glance. Days with more completed habits appear darker/more
    saturated, creating a visual pattern of dedication.
    
    The psychology: Users want to "keep the chain going" and not
    break their visual streak.
    
    Args:
        habits: List of all habit objects
    """
    today = date.today()
    year, month = today.year, today.month
    month_name = today.strftime("%B %Y")
    
    # Get calendar structure (weeks as rows, starting Sunday)
    cal = calendar.Calendar(firstweekday=6)
    month_calendar = cal.monthdayscalendar(year, month)
    
    # ── STEP 1: Count completions per day ──
    # This creates the "heatmap" intensity
    day_counts = {}
    for h in habits:
        for d_str in h.completions:
            try:
                dd = date.fromisoformat(d_str)
                if dd.year == year and dd.month == month:
                    day_counts[dd.day] = day_counts.get(dd.day, 0) + 1
            except (ValueError, TypeError):
                # Skip invalid dates gracefully
                continue
    
    # ── STEP 2: Build HTML grid ──
    total_habits = max(len(habits), 1)  # Avoid division by zero
    
    # Day of week headers
    day_labels = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    header_html = "".join(
        f'<div style="text-align:center;font-size:10px;font-weight:600;'
        f'color:var(--text2);padding-bottom:8px;text-transform:uppercase;'
        f'letter-spacing:0.5px;">{d}</div>'
        for d in day_labels
    )
    
    # Calendar cells
    cells_html = header_html
    for week in month_calendar:
        for day_num in week:
            if day_num == 0:
                cells_html += '<div></div>'
                continue
            
            # Calculate intensity based on completion ratio
            count = day_counts.get(day_num, 0)
            ratio = min(count / total_habits, 1.0)
            
            # Color interpolation: more completions = more saturated purple
            alpha = 0.08 + (ratio * 0.4)  # Range: 0.08 to 0.48
            bg_color = f"rgba(123, 97, 255, {alpha})"
            
            # Text color: darker if high completion, lighter if low
            text_color = "var(--text)" if ratio > 0.3 else "var(--text2)"
            
            # Border: accent color for today, subtle otherwise
            border = "0.5px solid var(--border2)"
            if day_num == today.day:
                border = "2px solid var(--accent2)"
            
            # Opacity for future days
            opacity = "0.3" if day_num > today.day else "1"
            
            cells_html += (
                f'<div class="calendar-cell'
                f'{" today" if day_num == today.day else ""}" '
                f'style="aspect-ratio:1;background:{bg_color};'
                f'border:{border};color:{text_color};opacity:{opacity};'
                f'font-size:12px;font-weight:600;'
                f'transition:all 0.2s ease;'
                f'" title="{count} habits completed">'
                f'{day_num}</div>'
            )
    
    # ── STEP 3: Add legend ──
    legend_html = '''
    <div style="display:flex;align-items:center;gap:8px;margin-top:12px;
                font-size:11px;color:var(--text2);justify-content:center;">
        <span style="opacity:0.6">Less</span>
        <div style="display:flex;gap:3px;">
            <div style="width:12px;height:12px;border-radius:3px;
                        background:rgba(123,97,255,0.1);"></div>
            <div style="width:12px;height:12px;border-radius:3px;
                        background:rgba(123,97,255,0.2);"></div>
            <div style="width:12px;height:12px;border-radius:3px;
                        background:rgba(123,97,255,0.35);"></div>
            <div style="width:12px;height:12px;border-radius:3px;
                        background:rgba(123,97,255,0.5);"></div>
        </div>
        <span>More</span>
    </div>
    '''
    
    # ── STEP 4: Combine and render ──
    html = f'''
    <div class="glass-card fade-in" style="padding:20px;">
        <div style="display:flex;justify-content:space-between;
                    align-items:center;margin-bottom:16px;">
            <p style="font-size:15px;font-weight:700;color:var(--text);
                      margin:0;">{month_name}</p>
            <p style="font-size:12px;color:var(--text2);margin:0;">
                {sum(day_counts.values())} total completions
            </p>
        </div>
        <div style="display:grid;grid-template-columns:repeat(7,1fr);
                    gap:4px;">{cells_html}</div>
        {legend_html}
    </div>
    '''
    
    st.markdown(html, unsafe_allow_html=True)


def render_habit_calendar(habit: Habit):
    """
    Shows a monthly calendar for a SINGLE habit.
    
    Unlike the global calendar, this uses a clear green/red system:
    - Green: Habit was completed
    - Red: Habit was missed (habit existed but not done)
    - Gray: Not applicable (future or before habit existed)
    
    This binary view helps users see their consistency pattern
    and identify where they tend to slip up.
    
    Args:
        habit: Single habit object to visualize
    """
    today = date.today()
    year, month = today.year, today.month
    month_name = today.strftime("%B %Y")
    
    # Get habit's completed days for this month
    habit_days = habit.get_calendar_month(year, month)
    
    # Parse creation date
    try:
        created = date.fromisoformat(habit.created_at)
    except (ValueError, TypeError):
        created = today  # Fallback to today if invalid
    
    # Get calendar structure
    cal = calendar.Calendar(firstweekday=6)
    month_calendar = cal.monthdayscalendar(year, month)
    
    # ── STEP 1: Calculate stats ──
    # Days since habit creation (or start of month, whichever is later)
    month_start = date(year, month, 1)
    effective_start = max(created, month_start)
    
    # Count completed and missed days
    days_since_creation = (today - effective_start).days + 1 if effective_start <= today else 0
    completed_count = sum(1 for day in range(1, today.day + 1) if habit_days.get(day))
    missed_count = days_since_creation - completed_count - (1 if habit.is_completed_today() else 0)
    
    # Completion rate for this month
    possible_days = max(days_since_creation, 1)
    completion_rate = round((completed_count / possible_days) * 100, 1)
    
    # ── STEP 2: Build calendar grid ──
    day_labels = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    header_html = "".join(
        f'<div style="text-align:center;font-size:10px;font-weight:600;'
        f'color:var(--text2);padding-bottom:8px;text-transform:uppercase;'
        f'letter-spacing:0.5px;">{d}</div>'
        for d in day_labels
    )
    
    cells_html = header_html
    for week in month_calendar:
        for day_num in week:
            cells_html += render_calendar_cell(
                day_num, year, month, habit_days, created,
                is_empty=(day_num == 0)
            )
    
    # ── STEP 3: Build stats bar ──
    stats_html = f'''
    <div style="display:flex;gap:16px;margin-top:16px;
                padding-top:16px;border-top:1px solid var(--border2);">
        <div style="text-align:center;flex:1;">
            <div style="font-size:20px;font-weight:700;color:#10B981;">{completed_count}</div>
            <div style="font-size:11px;color:var(--text2);">Completed</div>
        </div>
        <div style="text-align:center;flex:1;">
            <div style="font-size:20px;font-weight:700;color:#EF4444;">{missed_count}</div>
            <div style="font-size:11px;color:var(--text2);">Missed</div>
        </div>
        <div style="text-align:center;flex:1;">
            <div style="font-size:20px;font-weight:700;color:var(--accent2);">{completion_rate}%</div>
            <div style="font-size:11px;color:var(--text2);">Rate</div>
        </div>
        <div style="text-align:center;flex:1;">
            <div style="font-size:20px;font-weight:700;color:#F5A623;">{habit.get_current_streak()}</div>
            <div style="font-size:11px;color:var(--text2);">Streak</div>
        </div>
    </div>
    '''
    
    # ── STEP 4: Add legend ──
    legend_html = '''
    <div style="display:flex;align-items:center;gap:12px;margin-top:12px;
                font-size:11px;color:var(--text2);justify-content:center;">
        <div style="display:flex;align-items:center;gap:4px;">
            <div style="width:12px;height:12px;border-radius:3px;
                        background:rgba(16,185,129,0.25);border:1px solid rgba(16,185,129,0.5);"></div>
            <span>Done</span>
        </div>
        <div style="display:flex;align-items:center;gap:4px;">
            <div style="width:12px;height:12px;border-radius:3px;
                        background:rgba(239,68,68,0.1);border:0.5px solid rgba(239,68,68,0.3);"></div>
            <span>Missed</span>
        </div>
    </div>
    '''
    
    # ── STEP 5: Combine and render ──
    html = f'''
    <div class="glass-card fade-in" style="padding:20px;">
        <div style="display:flex;justify-content:space-between;
                    align-items:center;margin-bottom:16px;">
            <div>
                <p style="font-size:15px;font-weight:700;color:var(--text);
                          margin:0;">{month_name}</p>
                <p style="font-size:12px;color:var(--text2);margin:0;">
                    {habit.emoji} {habit.name}
                </p>
            </div>
        </div>
        <div style="display:grid;grid-template-columns:repeat(7,1fr);
                    gap:4px;">{cells_html}</div>
        {stats_html}
        {legend_html}
    </div>
    '''
    
    st.markdown(html, unsafe_allow_html=True)


def render_streak_visualization(habit: Habit):
    """
    Creates a visual streak bar showing recent activity.
    
    Shows the last 30 days as a horizontal bar with:
    - Green blocks for completed days
    - Red blocks for missed days
    - Current streak highlighted
    
    This horizontal view is great for seeing patterns and trends
    that might not be obvious in a calendar grid.
    
    Args:
        habit: Habit object to visualize
    """
    today = date.today()
    days_to_show = 30
    
    # Build list of last N days
    day_data = []
    for i in range(days_to_show - 1, -1, -1):
        d = today - timedelta(days=i)
        is_completed = d.isoformat() in habit.completions
        is_future = d > today
        day_data.append({
            "date": d,
            "completed": is_completed,
            "future": is_future,
            "day_num": d.day
        })
    
    # Build HTML
    cells_html = ""
    for day in day_data:
        if day["future"]:
            bg = "rgba(128,128,128,0.1)"
            border = "none"
        elif day["completed"]:
            bg = "rgba(16, 185, 129, 0.6)"
            border = "1px solid rgba(16, 185, 129, 0.8)"
        else:
            bg = "rgba(239, 68, 68, 0.3)"
            border = "1px solid rgba(239, 68, 68, 0.5)"
        
        cells_html += (
            f'<div style="flex:1;aspect-ratio:1;min-width:8px;max-width:20px;'
            f'background:{bg};border:{border};border-radius:3px;'
            f'transition:all 0.2s ease;" '
            f'title="{day["date"].strftime("%b %d")}: {"✓" if day["completed"] else "✗"}">'
            f'</div>'
        )
    
    html = f'''
    <div style="margin:16px 0;">
        <div style="display:flex;gap:2px;align-items:center;">{cells_html}</div>
        <div style="display:flex;justify-content:space-between;margin-top:4px;
                    font-size:10px;color:var(--text2);">
            <span>{(today - timedelta(days=29)).strftime("%b %d")}</span>
            <span>Today</span>
        </div>
    </div>
    '''
    
    st.markdown(html, unsafe_allow_html=True)