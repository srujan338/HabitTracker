# UI Contract: Habit Tracker (Streamlit)

Since this is a Streamlit application, the "contracts" define the UI layout and interaction components.

## Main Dashboard
- **Sidebar**:
  - App Title: "Habit Builder"
  - Summary Metrics: Total Habits, Active Streaks.
- **Main View**:
  - **Habit List Table**: Displays Name, Current Streak, Longest Streak, and a "Complete" button.
  - **Add Habit Form**: Text input for name + "Add" button.
  - **Statistics Section**: Visual summary of consistency.

## Components & Interactions

### `Add Habit` Component
- **Input**: Text field (Label: "New Habit Name").
- **Action**: Button (Label: "Add").
- **Success**: Habit appears in list; input clears.
- **Error**: Shows warning if name is duplicate or empty.

### `Habit List` Component
- **Display**: Columns [Habit, Streak, Max, Action].
- **Action**: "Mark Complete" button for each row.
- **Behavior**: 
  - If completed today, button is disabled or hidden.
  - If not completed, clicking adds today to completions and refreshes view.

### `Delete Habit` Component
- **Action**: Small trash icon or "Delete" button next to each habit.
- **Confirmation**: Simple Streamlit confirmation dialog or immediate removal (beginner friendly).

## Formatting
- Dates: YYYY-MM-DD.
- Streaks: "X days".
