"""
=============================================================================
MENTORSHIP NOTE: CALENDAR RENDERING
=============================================================================
Visualizing data is key! These functions turn lists of dates into 
beautiful, interactive grids. 

We use 'st.markdown' with 'unsafe_allow_html=True' to inject custom HTML/CSS
grids because standard Streamlit doesn't have a "Habit Calendar" widget yet.
=============================================================================
"""

import streamlit as st
import calendar
from datetime import date
from src.habits import Habit

def render_global_calendar(habits: list):
    """
    Shows all activity across all habits in a single monthly grid.
    Days are darker/lighter based on how many habits were finished.
    """
    today = date.today()
    year, month = today.year, today.month
    
    # We use Python's built-in 'calendar' to get the structure of the month
    cal = calendar.Calendar(firstweekday=6) # Sunday start
    days_in_month = cal.monthdayscalendar(year, month)

    # 1. Prepare data: Count completions per day
    n_habits = max(len(habits), 1)
    day_counts = {}
    for h in habits:
        for d_str in h.completions:
            try:
                dd = date.fromisoformat(d_str)
                if dd.year == year and dd.month == month:
                    day_counts[dd.day] = day_counts.get(dd.day, 0) + 1
            except (ValueError, TypeError):
                continue

    # 2. Build the HTML Grid
    day_labels = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    header_cells = "".join(
        f'<div style="text-align:center;font-size:10px;font-weight:600;color:var(--text3);padding-bottom:6px;">{d}</div>'
        for d in day_labels
    )

    cells = header_cells
    for week in days_in_month:
        for day_num in week:
            if day_num == 0:
                cells += '<div></div>' # Empty space for days outside this month
                continue
            
            count = day_counts.get(day_num, 0)
            ratio = min(count / n_habits, 1.0)
            
            # THE GLASSY COLOR LOGIC
            # We vary the transparency based on completions
            bg = f"rgba(123, 97, 255, {0.1 + ratio * 0.8})"
            border = "0.5px solid var(--border2)"
            txt = "var(--text)" if ratio > 0.4 else "var(--text2)"

            if day_num == today.day:
                border = "2px solid var(--accent2)" # Highlight TODAY

            cells += (
                f'<div style="aspect-ratio:1;background:{bg};border:{border};'
                f'border-radius:8px;display:flex;align-items:center;justify-content:center;'
                f'font-size:12px;font-weight:700;color:{txt};transition:all 0.3s;">'
                f'{day_num}</div>'
            )

    # 3. Combine into final layout
    month_label = today.strftime("%B %Y")
    html = (
        f'<div class="glass-card" style="padding:20px;">'
        f'<p style="font-size:15px;font-weight:700;margin-bottom:16px;">{month_label}</p>'
        f'<div style="display:grid;grid-template-columns:repeat(7,1fr);gap:6px;">{cells}</div>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)

def render_habit_calendar(habit: Habit):
    """
    Shows a monthly grid for a SINGLE habit.
    Green = Done, Red = Missed.
    """
    today = date.today()
    year, month = today.year, today.month
    cal = calendar.Calendar(firstweekday=6)
    days_in_month = cal.monthdayscalendar(year, month)
    habit_days = habit.get_calendar_month(year, month)
    
    try:
        created = date.fromisoformat(habit.created_at)
    except:
        created = date.today()

    day_labels = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    header_cells = "".join(
        f'<div style="text-align:center;font-size:10px;font-weight:700;color:var(--text3);padding-bottom:8px;">{d.upper()}</div>'
        for d in day_labels
    )

    cells = header_cells
    for week in days_in_month:
        for day_num in week:
            if day_num == 0:
                cells += '<div></div>'
                continue
            
            this_date = date(year, month, day_num)
            is_today = this_date == today
            is_future = this_date > today
            before_created = this_date < created

            # Logic for color coding
            if before_created or is_future:
                bg, border, txt = "transparent", "0.5px solid var(--border)", "var(--text3)"
            elif habit_days.get(day_num):
                bg, border, txt = "rgba(107,203,119,0.25)", "0.5px solid var(--success)", "var(--success)"
            else:
                bg, border, txt = "rgba(255,107,107,0.15)", "0.5px solid var(--danger)", "var(--danger)"

            if is_today:
                border = "2px solid var(--accent2)"

            cells += (
                f'<div style="aspect-ratio:1;background:{bg};border:{border};'
                f'border-radius:10px;display:flex;align-items:center;justify-content:center;'
                f'font-size:13px;font-weight:700;color:{txt}; transition:all 0.3s;">'
                f'{day_num}</div>'
            )

    month_label = today.strftime("%B %Y")
    html = (
        f'<div class="glass-card" style="padding:20px;">'
        f'<p style="font-size:15px;font-weight:700;margin-bottom:16px;">{month_label}</p>'
        f'<div style="display:grid;grid-template-columns:repeat(7,1fr);gap:6px;">{cells}</div>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)
