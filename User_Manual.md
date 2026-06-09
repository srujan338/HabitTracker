# User Manual

## Internship Task Manager

### Introduction

Internship Task Manager is a simple application that helps users organize and track their daily tasks. Users can create tasks, view existing tasks, update task status, and remove tasks that are no longer needed.

---

## Features

* Add new tasks
* View all tasks
* Mark tasks as completed
* Delete tasks
* Store task information locally

---

## Starting the Application

Run the application:

```bash
python main.py
```

---

## Main Menu

After launching the application, users will see the following menu:

```text
1. Add Task
2. View Tasks
3. Mark Task as Completed
4. Delete Task
5. Exit
```

Select an option by entering the corresponding number.

---

## Adding a Task

1. Select option `1`.
2. Enter a task title.
3. Enter a task description.
4. The task will be added to the task list.

Example:

```text
Enter Task Title:
Learn Python

Enter Task Description:
Complete Python fundamentals course
```

---

## Viewing Tasks

1. Select option `2`.
2. All available tasks will be displayed.

Example:

```text
ID: 1
Title: Learn Python
Description: Complete Python fundamentals course
Status: Pending
```

---

## Marking a Task as Completed

1. Select option `3`.
2. Enter the task ID.
3. The task status will be updated to Completed.

Example:

```text
Enter Task ID: 1

Task marked as completed.
```

---

## Deleting a Task

1. Select option `4`.
2. Enter the task ID.
3. The task will be removed from the system.

Example:

```text
Enter Task ID: 1

Task deleted successfully.
```

---

## Exiting the Application

Select option `5` to safely close the application.

---

## Troubleshooting

### Application Does Not Start

Verify Python is installed:

```bash
python --version
```

### Task Data Not Saving

Ensure the application has permission to create and modify the task storage file.

---

## Support

For issues, feature requests, or bug reports, create an issue in the project repository.
