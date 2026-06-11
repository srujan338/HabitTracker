<!--
Sync Impact Report:
Version change: 0.1.0 -> 1.0.0
List of modified principles:
- I. Library-First -> I. Beginner Friendly
- II. CLI Interface -> II. Python First
- III. Test-First -> III. PEP8 Compliance
- IV. Integration Testing -> IV. JSON Storage
- V. Simplicity -> V. Modular Design
Added sections:
- VI. Minimal Dependencies
- VII. Readability Focused
- VIII. Documentation First
Templates requiring updates:
- .specify/templates/plan-template.md (✅ already generic)
- .specify/templates/spec-template.md (✅ already generic)
- .specify/templates/tasks-template.md (✅ already generic)
Follow-up TODOs:
- None
-->

# Habit Builder App Constitution

## Core Principles

### I. Beginner Friendly
Code must be written with beginners in mind. Use clear naming, avoid overly complex abstractions, and provide helpful comments where the "why" isn't obvious from the "what".

### II. Python First
The primary programming language for this project is Python. All core logic and features must be implemented in Python unless a specific, justified need for another language arises.

### III. PEP8 Compliance
All Python code must follow the PEP8 style guide. Consistency in formatting, naming, and structure is mandatory to ensure code quality and readability.

### IV. JSON Storage
Data persistence must use JSON format. Storage files should be well-structured, easy to read, and modular to allow for future expansion.

### V. Modular Design
Write small, focused, and modular functions. Each function should perform a single task. This promotes reusability, easier testing, and clearer logic flow.

### VI. Minimal Dependencies
Keep external dependencies to an absolute minimum. Prioritize Python's standard library. Any new dependency must be justified and approved.

### VII. Readability Focused
Prioritize code readability over clever optimizations. If a piece of code is fast but hard to understand, it should be refactored for clarity unless performance is a critical, proven bottleneck.

### VIII. Documentation First
Every feature must be documented. This includes user-facing manuals, inline docstrings for functions, and high-level architectural descriptions in the repository.

## Additional Constraints

### Technology Stack
- **Language**: Python 3.10+
- **Storage**: Local JSON files
- **Style**: PEP8 (Flake8 / Black recommended)

## Development Workflow

### Quality Gates
1. **Lint Check**: Code MUST pass PEP8 linting.
2. **Doc Check**: New features MUST include documentation updates.
3. **Complexity Review**: Code MUST be beginner-friendly; complex logic MUST be justified.

## Governance
The Constitution is the supreme guidance for the Habit Builder App project. Amendments require documentation and a version bump.

**Versioning Policy**:
- MAJOR: Removal or redefinition of core principles.
- MINOR: New principles or significant workflow changes.
- PATCH: Clarifications and non-semantic refinements.

**Version**: 1.0.0 | **Ratified**: 2026-06-09 | **Last Amended**: 2026-06-09
