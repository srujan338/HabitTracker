# Tasks: Habit Tracker

**Input**: Design documents from `/specs/001-habit-tracker/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Pytest is specified in the technical context. Tests will be written for core logic and storage.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths shown below assume single project - adjust based on plan.md structure

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 [P] Create project structure: `src/`, `tests/unit/`, `assets/`
- [X] T002 [P] Initialize Python project and install `streamlit` and `pytest`
- [X] T003 [P] Configure `.gitignore` to exclude `__pycache__` and `habits.json` (for local development)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure for storage and habit manipulation

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 [P] Implement JSON storage handler in `src/storage.py` (load/save habits)
- [X] T005 [P] Create unit test for storage in `tests/unit/test_storage.py`
- [X] T006 [P] Implement `Habit` data class or dictionary structure in `src/habits.py`
- [X] T007 [P] Setup base `main.py` with Streamlit sidebar and title

**Checkpoint**: Foundation ready - storage and basic habit structures are in place.

---

## Phase 3: User Story 1 - Habit Management (Priority: P1) 🎯 MVP

**Goal**: Create and view habits

**Independent Test**: Add a habit via the UI and see it appear in the habit list table.

### Tests for User Story 1

- [X] T008 [P] [US1] Write unit tests for habit creation in `tests/unit/test_habits.py`
- [X] T009 [P] [US1] Write unit tests for storage persistence after creation in `tests/unit/test_storage.py`

### Implementation for User Story 1

- [X] T010 [US1] Implement habit creation logic in `src/habits.py` (ensure unique names)
- [X] T011 [US1] Implement "Add Habit" form in `main.py`
- [X] T012 [US1] Implement habit list display (table) in `main.py`
- [X] T013 [US1] Integrate "Add Habit" action with storage save in `main.py`

**Checkpoint**: User Story 1 is functional - habits can be created and viewed persistently.

---

## Phase 4: User Story 2 - Completion Tracking & Streaks (Priority: P1)

**Goal**: Mark habits as completed and calculate streaks

**Independent Test**: Click "Mark Complete" for a habit and verify its current streak increases by 1.

### Tests for User Story 2

- [X] T014 [P] [US2] Write unit tests for streak calculation logic in `tests/unit/test_habits.py` (successive days, missed days)
- [X] T015 [P] [US2] Write unit tests for "Longest Streak" update logic in `tests/unit/test_habits.py`

### Implementation for User Story 2

- [X] T016 [US2] Implement streak calculation function in `src/habits.py` (dynamic calculation from completion dates)
- [X] T017 [US2] Implement "Mark Complete" logic in `src/habits.py` (prevents double-completion on same day)
- [X] T018 [US2] Update habit list in `main.py` to include "Mark Complete" button and streak counts
- [X] T019 [US2] Add summary metrics (Active Streaks, Total Habits) to `main.py` sidebar

**Checkpoint**: User Story 2 is functional - streaks are tracked and displayed.

---

## Phase 5: User Story 3 - Cleanup (Priority: P2)

**Goal**: Delete habits from the list

**Independent Test**: Click "Delete" for a habit and verify it is removed from the list and storage.

### Tests for User Story 3

- [X] T020 [P] [US3] Write unit tests for habit deletion in `tests/unit/test_habits.py`
- [X] T021 [P] [US3] Write unit tests for storage sync after deletion in `tests/unit/test_storage.py`

### Implementation for User Story 3

- [X] T022 [US3] Implement habit deletion logic in `src/habits.py`
- [X] T023 [US3] Update habit list in `main.py` to include a "Delete" button for each row
- [X] T024 [US3] Implement confirmation/refresh logic after deletion in `main.py`

**Checkpoint**: User Story 3 is functional - habits can be managed and removed.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements and final documentation

- [X] T025 [P] Apply PEP8 linting and formatting (Black/Flake8) across all `.py` files
- [X] T026 [P] Add inline docstrings to all functions in `src/habits.py` and `src/storage.py`
- [X] T027 [P] Finalize `README.md` with instructions from `quickstart.md`
- [X] T028 Run all tests via `pytest` and verify 100% pass rate

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Phase 1 completion.
- **User Story 1 (Phase 3)**: Depends on Phase 2 completion (Storage/Habit base).
- **User Story 2 (Phase 4)**: Depends on Phase 3 completion (Needs viewing/creation base).
- **User Story 3 (Phase 5)**: Depends on Phase 3 completion.
- **Polish (Phase 6)**: Depends on all user stories being complete.

### Parallel Opportunities

- T001, T002, T003 in Phase 1 can run in parallel.
- T004, T005, T006, T007 in Phase 2 can run in parallel.
- Test tasks (T008, T009) can be written in parallel with UI setup (T011, T012).
- Phase 4 and Phase 5 can technically run in parallel once Phase 3 is complete.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Setup (Phase 1).
2. Complete Foundational (Phase 2).
3. Complete User Story 1 (Phase 3).
4. **VALIDATE**: Run `streamlit run main.py` and verify habit creation/persistence.

### Incremental Delivery

1. Foundation ready.
2. Habit Management ready (US1) -> **MVP!**
3. Add Streak Tracking (US2).
4. Add Cleanup (US3).
5. All features verified.
