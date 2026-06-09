import streamlit as st
from datetime import date
from src.storage import load_habits, save_habits
from src.habits import Habit, add_habit, delete_habit

st.set_page_config(page_title="Habit Builder", layout="wide")

def main():
    st.title("Habit Builder")
    
    # Sidebar
    st.sidebar.header("Navigation")
    st.sidebar.info("Track your daily habits and build consistency.")
    
    # Load habits
    habits_data = load_habits()
    habits = [Habit.from_dict(h) for h in habits_data]
    
    # Sidebar Metrics
    st.sidebar.subheader("Metrics")
    active_streaks = [h.get_current_streak() for h in habits if h.get_current_streak() > 0]
    st.sidebar.metric("Total Habits", len(habits))
    st.sidebar.metric("Active Streaks", len(active_streaks))
    if active_streaks:
        st.sidebar.metric("Best Streak", max(active_streaks))

    # US1: Add Habit Form
    with st.expander("Add New Habit", expanded=True):
        with st.form("add_habit_form", clear_on_submit=True):
            new_habit_name = st.text_input("Habit Name", placeholder="e.g., Read for 30 minutes")
            submit_button = st.form_submit_button("Add Habit")
            
            if submit_button:
                if new_habit_name:
                    _, error = add_habit(habits, new_habit_name)
                    if error:
                        st.error(error)
                    else:
                        save_habits([h.to_dict() for h in habits])
                        st.success(f"Habit '{new_habit_name}' added!")
                        st.rerun()
                else:
                    st.warning("Please enter a habit name.")

    # US1: Habit List Display
    st.subheader("Your Habits")
    if not habits:
        st.info("No habits added yet. Start by adding one above!")
    else:
        for habit in habits:
            col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
            with col1:
                st.write(f"**{habit.name}**")
            with col2:
                st.write(f"🔥 {habit.get_current_streak()}")
            with col3:
                st.write(f"🏆 {habit.longest_streak}")
            with col4:
                # US2: Mark Complete Logic
                is_completed_today = date.today().isoformat() in habit.completions
                if st.button("Complete", key=f"complete_{habit.name}", disabled=is_completed_today):
                    if habit.mark_complete():
                        save_habits([h.to_dict() for h in habits])
                        st.success(f"Way to go! '{habit.name}' completed.")
                        st.rerun()
            with col5:
                # US3: Delete Habit Logic
                if st.button("🗑️", key=f"delete_{habit.name}"):
                    if delete_habit(habits, habit.name):
                        save_habits([h.to_dict() for h in habits])
                        st.warning(f"Habit '{habit.name}' deleted.")
                        st.rerun()
            st.divider()

if __name__ == "__main__":
    main()
