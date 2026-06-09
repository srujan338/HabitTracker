# AGENTS.md

# Habit Builder App

## Project Overview

Habit Builder App helps users develop positive habits by tracking daily consistency, streaks, and completion rates.

This project is intended as both a productivity tool and a learning project for software development fundamentals.

---

## Objectives

* Help users build habits through consistent tracking.
* Provide meaningful progress insights.
* Maintain a simple and intuitive user experience.
* Serve as a beginner-friendly codebase.

---

## System Architecture

```text
User
 ↓
Habit Management Layer
 ↓
Progress Tracking Layer
 ↓
Storage Layer
 ↓
JSON Database
```

---

## Core Features

### Habit Management

* Create habits
* View habits
* Update habits
* Delete habits

### Progress Tracking

* Daily completion tracking
* Streak calculation
* Completion statistics

### Analytics

* Longest streak
* Completion percentage
* Active habit count

---

## Habit Data Structure

```python
{
    "id": 1,
    "name": "Exercise",
    "frequency": "Daily",
    "current_streak": 5,
    "longest_streak": 12,
    "completed_today": False
}
```

---

## Coding Standards

### General Rules

* Follow PEP 8.
* Use meaningful names.
* Keep functions focused on one responsibility.
* Avoid duplicated logic.
* Write readable code.

### Function Naming

```python
def add_habit():
    pass

def complete_habit():
    pass

def calculate_streak():
    pass
```

---

## Suggested Project Structure

```text
habit-builder/
│
├── main.py
├── habits.json
├── README.md
├── USER_MANUAL.md
├── AGENTS.md
│
├── src/
│   ├── habits.py
│   ├── statistics.py
│   ├── storage.py
│   └── utils.py
│
└── assets/
```

---

## Testing Requirements

Verify:

* Habit creation
* Habit deletion
* Daily completion tracking
* Streak calculations
* Statistics generation
* Data persistence

---

## Future Enhancements

### Version 2

* Categories
* Weekly goals
* Monthly reports

### Version 3

* User authentication
* Cloud synchronization

### Version 4

* Mobile application

### Version 5

* AI-powered habit recommendations

---

## Development Principles

1. **Beginner Friendly**: Keep code accessible to learners.
2. **Python First**: Standardize on Python.
3. **PEP8 Compliance**: Follow Python style guides strictly.
4. **JSON Storage**: Use JSON for data persistence.
5. **Modular Design**: Build small, focused functions.
6. **Minimal Dependencies**: Prioritize the standard library.
7. **Readability Focused**: Clarity over optimization.
8. **Documentation First**: Document every feature and change.

---

## Contribution Guidelines

* Keep features beginner-friendly.
* Update documentation when changing functionality.
* Write descriptive commit messages.
* Test before submitting pull requests.
