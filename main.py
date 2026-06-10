"""
=============================================================================
CHAPTER 2: THE SWITCHBOARD (main.py)
=============================================================================
Welcome to your app's Brain. 

I've structured this file like a book. Read the "Mentorship Notes" to learn
the industry secrets of building great apps!

Step 1: Imports (Bringing in your tools)
Step 2: Design (Applying the iOS Glass skin)
Step 3: Main Engine (The Logic that runs everything)
=============================================================================
"""

import streamlit as st
import os
from datetime import date

# ── STEP 1: MODULAR IMPORTS ── 
# MENTORSHIP NOTE: We keep logic in different files to stay organized.
# If one file gets too big, it's hard to fix bugs!
from src.habits import Habit, add_habit, delete_habit
from src.storage import load_habits, save_habits
from src.ui_components import render_top_nav, glass_card_start, glass_card_end, rank_badge
from src.calendars import render_global_calendar, render_habit_calendar

# Configure the basics of the browser tab
st.set_page_config(
    page_title="habit.space",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── STEP 2: DESIGN ENGINE ── 

def apply_ios_skin():
    """
    MENTORSHIP NOTE: 
    This function "injects" our CSS into the webpage.
    We use st.html() because it's safer and cleaner than st.markdown().
    """
    theme = st.session_state.get("theme", "Dark")
    
    # Define our color palette based on Dark/Light mode
    if theme == "Dark":
        palette = """
        :root {
            --bg: linear-gradient(135deg, #0D0F14 0%, #1A1C25 100%);
            --glass: rgba(25, 28, 38, 0.6);
            --glass-heavy: rgba(15, 17, 23, 0.85);
            --text: #F8FAFC;
            --text2: #94A3B8;
            --accent2: #7B61FF;
            --success: #6BCB77;
            --danger: #FF6B6B;
            --border2: rgba(255, 255, 255, 0.1);
            --shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        }
        """
    else:
        palette = """
        :root {
            --bg: linear-gradient(135deg, #F8FAFC 0%, #E2E8F0 100%);
            --glass: rgba(255, 255, 255, 0.65);
            --glass-heavy: rgba(255, 255, 255, 0.9);
            --text: #1E293B;
            --text2: #475569;
            --accent2: #6366F1;
            --success: #10B981;
            --danger: #EF4444;
            --border2: rgba(0, 0, 0, 0.08);
            --shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.08);
        }
        """

    # Load the design file
    try:
        with open("assets/style.css", "r") as f:
            design_code = f.read()
    except:
        design_code = ""

    # Inject into the app!
    st.html(f"<style>{palette}\n{design_code}</style>")

# ── STEP 3: DATA INITIALIZATION ── 

def start_memory():
    """Streamlit 're-runs' every time you click. We need to remember data!"""
    if "theme" not in st.session_state: st.session_state.theme = "Dark"
    if "active_page" not in st.session_state: st.session_state.active_page = "Today"
    if "habits" not in st.session_state:
        raw_data = load_habits()
        st.session_state.habits = [Habit.from_dict(h) for h in raw_data]

def save_memory():
    """Saves everything to the habits.json file."""
    save_habits([h.to_dict() for h in st.session_state.habits])

# ── CHAPTER 3: THE PAGES ── 

def show_page_today(habits):
    """The first thing you see! Your daily checklist."""
    st.title("Today's Focus")
    
    # ── METRICS ──
    done = [h for h in habits if h.is_completed_today()]
    cols = st.columns(3)
    cols[0].metric("Total", len(habits))
    cols[1].metric("Done Today", len(done))
    cols[2].metric("Best Streak", f"{max((h.get_current_streak() for h in habits), default=0)} 🔥")

    # ── ACTIVITY GRID ──
    glass_card_start()
    st.markdown("### Monthly Momentum")
    render_global_calendar(habits)
    glass_card_end()

    # ── CHECKLIST ──
    for h in habits:
        is_done = h.is_completed_today()
        c1, c2, c3 = st.columns([6, 2, 2])
        with c1: st.markdown(f"### {h.emoji} {h.name}")
        with c2:
            if not is_done:
                if st.button("Check in", key=f"btn_{h.name}"):
                    h.mark_complete()
                    save_memory()
                    st.rerun()
            else:
                st.success("Completed!")
        with c3:
            if st.button("View Details", key=f"det_{h.name}"):
                st.session_state.selected_habit = h.name
                st.session_state.active_page = "Habit Detail"
                st.rerun()
        st.divider()

def show_page_manage(habits):
    """Where you add and remove habits."""
    st.title("Manage Habits")
    
    # ── CREATION BOX ──
    with st.container(border=True):
        st.markdown("### 🎯 Add New Goal")
        c1, c2, c3 = st.columns([4, 2, 2])
        name = c1.text_input("Goal Name", placeholder="e.g. Drink Water")
        type = c2.selectbox("Type", ["adopt", "quit"])
        emoji = c3.selectbox("Icon", ["📚", "🏃", "💧", "🧘", "🚭", "📵"])
        
        if st.button("Create Habit", type="primary", use_container_width=True):
            if name:
                add_habit(habits, name, type, emoji)
                save_memory()
                st.rerun()

    # ── LIST ──
    st.markdown("### Your Current Habits")
    for h in habits:
        rank = h.get_rank()
        c1, c2 = st.columns([8, 2])
        c1.markdown(f"**{h.emoji} {h.name}** ({h.habit_type})  \n{rank_badge(rank, text_only=True)}")
        if c2.button("Delete", key=f"del_{h.name}"):
            delete_habit(habits, h.name)
            save_memory()
            st.rerun()
        st.divider()

def show_page_detail(habits, name):
    """A deep dive into one specific habit."""
    habit = next((h for h in habits if h.name == name), None)
    if not habit: return

    if st.button("← Back to List"):
        st.session_state.active_page = "Today"
        st.rerun()

    st.title(f"{habit.emoji} {habit.name}")
    
    glass_card_start()
    render_habit_calendar(habit)
    glass_card_end()
    
    st.metric("All-time Success", f"{habit.get_total_completions()} times")

# ── CHAPTER 4: THE EXECUTION ── 

def main():
    # Initialize app
    start_memory()
    apply_ios_skin()
    
    # Navigation
    render_top_nav(
        st.session_state.habits, 
        st.session_state.active_page,
        st.session_state.theme
    )
    
    # Load data
    habits = st.session_state.habits
    page = st.session_state.active_page

    # Centered Column (The stage)
    _, center, _ = st.columns([1, 8, 1])
    
    with center:
        if page == "Today":
            show_page_today(habits)
        elif page == "My Habits":
            show_page_manage(habits)
        elif page == "Habit Detail":
            show_page_detail(habits, st.session_state.get("selected_habit"))
        elif page == "AI Coach":
            st.info("AI Coach is currently in maintenance mode.")

if __name__ == "__main__":
    main()
