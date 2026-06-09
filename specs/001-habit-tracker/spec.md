# Feature Specification: Habit Tracker

**Feature Branch**: `001-habit-tracker`

**Created**: 2026-06-09

**Status**: Draft

**Input**: User description: "Build a Habit Builder application. Users can create habits and track their completion daily. The system should allow users to: - Create habits - View habits - Mark habits as completed - Track current streaks - Track longest streaks - Delete habits The application should store data persistently. The primary goal is helping users build consistency through habit tracking. The application should be simple and beginner friendly."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Habit Management (Priority: P1)

As a user, I want to create and view my habits so that I can organize my daily routines.

**Why this priority**: Essential for the existence of the application; without habits to track, the app has no purpose.

**Independent Test**: User can add a habit named "Read" and immediately see it in their habit list.

**Acceptance Scenarios**:

1. **Given** no habits exist, **When** I add a habit named "Exercise", **Then** the habit list should contain "Exercise".
2. **Given** a list of habits, **When** I view the list, **Then** I should see all my created habits with their current status.

---

### User Story 2 - Completion Tracking & Streaks (Priority: P1)

As a user, I want to mark habits as completed and see my streaks so that I stay motivated to maintain consistency.

**Why this priority**: Core value proposition of the app. Tracking streaks is the primary motivator.

**Independent Test**: Mark a habit as completed today, and verify the current streak increases by 1.

**Acceptance Scenarios**:

1. **Given** a habit with a 2-day streak, **When** I mark it as completed today, **Then** the current streak should become 3 days.
2. **Given** a habit was completed yesterday, **When** I view it today, **Then** I should see the current streak and the longest streak achieved.

---

### User Story 3 - Cleanup (Priority: P2)

As a user, I want to delete habits I no longer wish to track so that my list remains relevant.

**Why this priority**: Necessary for long-term maintenance of the habit list.

**Independent Test**: Delete an existing habit and verify it no longer appears in the list.

**Acceptance Scenarios**:

1. **Given** a habit "Old Habit", **When** I delete it, **Then** it should be permanently removed from storage and the view.

## Clarifications

### Session 2026-06-09
- Q: Should habit names be unique within the application? → A: Names must be unique; prevent duplicates.
- Q: When marking a habit as completed, should the system allow past dates or only the current date? → A: Automatically use current system date.
- Q: What is the grace period for a streak before it is considered "broken"? → A: Break streak on first missed day.
- Q: How should time zones be handled for the daily reset? → A: Use local system time only.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow users to create a habit with a unique name.
- **FR-002**: System MUST persist all habit data to a JSON file.
- **FR-003**: System MUST allow users to mark a habit as completed for the current system date.
- **FR-004**: System MUST calculate the "Current Streak" based on consecutive days of completion.
- **FR-005**: System MUST track and persist the "Longest Streak" for each habit.
- **FR-006**: System MUST allow users to delete a habit.
- **FR-007**: System MUST display a list of all habits with their name, current streak, and longest streak.

### Key Entities

- **Habit**: Represents a recurring task to be tracked.
  - Attributes: Name (unique), Completion Dates (ISO-8601 list), Current Streak, Longest Streak.
  - Storage: Persisted as a list of habit objects in JSON.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can add a new habit and see it in the list in under 1 second.
- **SC-002**: Data persists correctly between application restarts.
- **SC-003**: Streak calculations accurately reflect the number of consecutive completion days.
- **SC-004**: System handles at least 50 habits without performance degradation.

## Assumptions

- **A-001**: Habits are tracked on a daily basis (resetting at local system midnight).
- **A-002**: A streak is broken if a single day is missed (no grace period).
- **A-003**: The application is a single-user system (no authentication required for MVP).
- **A-004**: The UI will be a simple command-line interface or text-based view as per the "beginner-friendly" and "simple" requirements.
-line interface or text-based view as per the "beginner-friendly" and "simple" requirements.
mple" requirements.
