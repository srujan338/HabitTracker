# AGENTS.md

## Project Overview

Internship Task Manager is a beginner-friendly task management application designed to teach software development fundamentals through practical implementation.

This document provides guidance for contributors, developers, and AI coding agents working on this repository.

---

## Project Goals

1. Maintain clean and readable code.
2. Prioritize simplicity over complexity.
3. Follow modular design principles.
4. Keep the project beginner-friendly.
5. Document all major changes.

---

## Architecture

```text
User
 ↓
Application Logic
 ↓
Storage Layer
 ↓
JSON File
```

### Components

#### Main Application

Responsible for:

* Application startup
* Menu navigation
* User interaction

#### Task Manager

Responsible for:

* Creating tasks
* Viewing tasks
* Updating tasks
* Deleting tasks

#### Storage Layer

Responsible for:

* Loading task data
* Saving task data
* File operations

---

## Coding Standards

### General

* Follow PEP 8 standards.
* Use meaningful variable names.
* Write small reusable functions.
* Avoid duplicate code.
* Add comments when logic is not obvious.

### Naming Conventions

Functions:

```python
def add_task():
    pass
```

Variables:

```python
task_id = 1
task_title = "Learn Git"
```

Constants:

```python
MAX_TASKS = 100
```

---

## Task Object Format

```python
{
    "id": 1,
    "title": "Learn Python",
    "description": "Complete Python course",
    "status": "Pending"
}
```

---

## Development Workflow

1. Create a feature branch.
2. Implement changes.
3. Test functionality.
4. Update documentation if required.
5. Commit using descriptive messages.
6. Submit merge request.

Example:

```bash
git checkout -b feature/add-task-priority
git add .
git commit -m "Add task priority support"
git push
```

---

## Future Enhancements

Potential improvements:

* Priority levels
* Task categories
* Search functionality
* Database integration
* REST API
* Web interface
* Authentication

---

## Testing Guidelines

Verify:

* Task creation works.
* Task updates work.
* Task deletion works.
* Data persistence works.
* Invalid inputs are handled correctly.

---

## Design Principles

* Simplicity first.
* Readability over optimization.
* Educational value is important.
* Modular code structure.
* Easy onboarding for new contributors.

---

## Contribution Rules

* Do not introduce unnecessary dependencies.
* Maintain backward compatibility where possible.
* Update documentation alongside features.
* Keep code beginner-friendly and easy to understand.
