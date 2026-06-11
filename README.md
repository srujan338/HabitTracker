# Habit Builder App

A simple, beginner-friendly habit-tracking application built with Python and Streamlit.

## Features
- **Create Habits**: Organize your daily routines with ease.
- **Track Completion**: Mark habits as completed each day.
- **Streaks**: Visualize your consistency with current and longest streak tracking.
- **Persistent Storage**: Your data is saved locally in a `habits.json` file.
- **Simple UI**: Intuitive web interface powered by Streamlit.

## Prerequisites
- Python 3.10 or later

## Setup
1. Clone the repository.
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application
Run the Streamlit app from the root directory:
```bash
streamlit run main.py
```

## Running Tests
To run the unit tests:
```bash
PYTHONPATH=. pytest tests/unit/
```

## Project Structure
- `main.py`: Entry point for the Streamlit application.
- `src/habits.py`: Core logic for habit management and streak calculation.
- `src/storage.py`: Handles local JSON data persistence.
- `requirements.txt`: List of Python dependencies.
- `specs/`: Project specification and planning documents.

## License
Educational purpose - feel free to use and learn!
