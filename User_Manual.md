# User Manual

# Habit Builder App

## Introduction

Habit Builder App is a simple habit-tracking application designed to help users build consistency and monitor personal growth.

Users can create habits, track daily progress, view streaks, and monitor completion rates.

---

## Features

* Add new habits
* View all habits
* Mark habits as completed
* Track daily streaks
* View progress statistics
* Delete habits

---

## Getting Started

### Run the Application

```bash
python main.py
```

---

## Main Menu

```text
1. Add Habit
2. View Habits
3. Complete Habit
4. View Statistics
5. Delete Habit
6. Exit
```

---

## Adding a Habit

Select option `1`.

Example:

```text
Habit Name: Exercise
Target Frequency: Daily
```

The habit will be added to your habit list.

---

## Viewing Habits

Select option `2`.

Example:

```text
ID: 1
Habit: Exercise
Current Streak: 5 Days
Completion Rate: 90%
Status: Active
```

---

## Completing a Habit

Select option `3`.

Enter the habit ID.

Example:

```text
Enter Habit ID: 1

Habit completed successfully.
```

The current streak and progress data will be updated automatically.

---

## Viewing Statistics

Select option `4`.

Statistics displayed:

* Total Habits
* Active Habits
* Longest Streak
* Completion Percentage

Example:

```text
Total Habits: 5
Longest Streak: 12 Days
Completion Rate: 84%
```

---

## Deleting a Habit

Select option `5`.

Enter the habit ID you wish to remove.

Example:

```text
Enter Habit ID: 3

Habit deleted successfully.
```

---

## Troubleshooting

### Application Does Not Start

Verify Python installation:

```bash
python --version
```

### Progress Not Saving

Ensure the application has permission to create and update storage files.

---

## Support

For bug reports, feature requests, or improvement suggestions, create an issue in the project repository.
