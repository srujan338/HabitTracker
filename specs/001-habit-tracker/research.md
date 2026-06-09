# Research: Habit Tracker

## Decision: Streamlit for Frontend
Streamlit will be used to build the web interface. It allows for rapid development of data-driven applications using only Python, which perfectly aligns with the "beginner friendly" and "minimal dependencies" goals.

**Rationale**: 
- Native Python support.
- Built-in components for forms, buttons, and tables.
- No need for complex HTML/JS/CSS knowledge.
- Simple state management.

**Alternatives Considered**:
- **Flask/Django**: Rejected due to higher complexity and overhead for a simple prototype.
- **Pure CLI**: Rejected as the user requested a "Streamlit" frontend in the plan input.

## Decision: JSON File Storage
Data will be stored in a local `habits.json` file.

**Rationale**:
- Human-readable and easily inspectable by beginners.
- No database setup required.
- Standard library `json` module is sufficient (minimal dependencies).

**Alternatives Considered**:
- **SQLite**: Considered for better data integrity but rejected to keep the storage "visible" and simple for beginners as per the constitution.

## Decision: Modular Python Structure
The application will follow a simple modular structure:
- `main.py`: Entry point for Streamlit.
- `src/habits.py`: Core logic for habit management (streaks, CRUD).
- `src/storage.py`: JSON file I/O handling.

**Rationale**:
- Encourages separation of concerns.
- Easy to test individual modules.
- Aligns with the constitution's "Modular Design" principle.

## Decision: Streak Logic
Streaks will be calculated dynamically based on the list of completion dates.

**Rationale**:
- Storing only dates and calculating streaks on the fly prevents data desynchronization.
- Simplifies the data model (only need `dates` list).

**Alternatives Considered**:
- **Storing Current/Longest Streak counts**: Rejected to avoid state sync issues; counts will be cached if performance becomes an issue (unlikely for <50 habits).
