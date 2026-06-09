# Internship Task Manager

A simple task management application built to learn the core concepts of software development while solving a real-world problem.

## 📌 Project Overview

Internship Task Manager helps users organize, track, and manage their daily tasks. The application allows users to create tasks, view existing tasks, update task status, and delete completed or unnecessary tasks.

This project is designed as a learning project that covers the fundamental concepts used in most software applications.

---

## 🎯 Objectives

- Learn programming fundamentals through a practical project
- Understand how data is stored and manipulated
- Learn CRUD operations (Create, Read, Update, Delete)
- Practice working with functions, loops, conditions, and data structures
- Understand how frontend, backend, and storage interact

---

## ✨ Features

### Task Management
- Add new tasks
- View all tasks
- Mark tasks as completed
- Delete tasks

### Task Information
Each task contains:
- Task ID
- Task Title
- Task Description
- Status (Pending / Completed)

### Future Enhancements
- Due dates
- Priority levels
- Categories
- User authentication
- Database integration
- Web interface
- Notifications

---

## 🛠️ Technologies Used

### Current Version
- Python
- JSON File Storage

### Future Versions
- HTML
- CSS
- JavaScript
- Flask / FastAPI
- SQLite / PostgreSQL
- Git & GitLab

---

## 📚 Concepts Learned

This project teaches the following programming concepts:

### Variables
Used to store task information.

### Lists
Used to store multiple tasks.

### Dictionaries
Used to represent task objects.

Example:

```python
task = {
    "id": 1,
    "title": "Learn Git",
    "status": "Pending"
}
```

### Conditions

```python
if task["status"] == "Pending":
    print("Task not completed")
```

### Loops

```python
for task in tasks:
    print(task["title"])
```

### Functions

```python
def add_task():
    pass
```

### CRUD Operations

- Create → Add Task
- Read → View Tasks
- Update → Mark Completed
- Delete → Remove Task

---

## 📂 Project Structure

```text
internship-task-manager/
│
├── main.py
├── tasks.json
├── README.md
│
├── src/
│   ├── task_manager.py
│   ├── storage.py
│   └── utils.py
│
└── assets/
```

---

## 🚀 How It Works

1. User enters a task.
2. Application stores the task.
3. User can view all tasks.
4. User can update task status.
5. User can delete tasks.
6. Data is saved for future use.

Workflow:

```text
User Input
     ↓
Task Manager
     ↓
Store Data
     ↓
Display Results
```

---

## 📝 Example Usage

### Add Task

```text
Enter task title:
Learn Python Basics
```

### View Tasks

```text
1. Learn Python Basics [Pending]
2. Complete Internship Project [Completed]
```

### Mark Task Complete

```text
Task ID: 1
Status Updated Successfully
```

---

## 🎓 Learning Outcome

After completing this project, a developer should understand:

- Basic programming logic
- Problem solving
- Data structures
- Functions
- CRUD operations
- File handling
- Project organization
- Version control with Git

These concepts form the foundation of most software applications and are transferable across programming languages such as Python, JavaScript, Java, C#, and Go.

---

## 📈 Future Roadmap

### Version 1
- Console-based application

### Version 2
- JSON data persistence

### Version 3
- Web-based interface

### Version 4
- Database integration

### Version 5
- Multi-user support

### Version 6
- Deployment to cloud

---

## 👨‍💻 Author

Built as a learning project to understand software development fundamentals and real-world application architecture.