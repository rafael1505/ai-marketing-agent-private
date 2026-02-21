# Feature Specification: Start Full Development Environment Task Audit

**Feature Branch**: `001-dev-env-task-audit`  
**Created**: 2025-02-19  
**Status**: Draft  
**Input**: User description: "There is a task called Start full development environment. It should start MongoDB, frontend and backend. However when I run it, it presents an error message. This task was created when the project was being developed in VSCode IDE, as we moved to Cursor it needs to be scanned and analysed whether any update is needed."

## Clarifications

### Session 2025-02-19

- Q: How should the start task run the full stack — Docker Compose only (all in containers), mixed (Mongo in Docker + local backend/frontend), or support both? → A: Docker Compose only.
- Q: Where should the canonical task definition live — .vscode/tasks.json only, Cursor-specific path, or both? → A: .vscode/tasks.json only.
- Q: What does "clear feedback" mean — explicit user-facing messages, command output only, or exit code only? → A: Explicit user-facing messages.
- Q: Should the Stop full development environment task be required or optional? → A: Required.
- Q: Should the canonical task labels include emoji or be plain text? → A: No emoji (plain "Start full development environment" and "Stop full development environment").

## User Scenarios & Testing *(mandatory)*

### User Story 1 - One-Click Start of Full Stack (Priority: P1)

A developer working in Cursor runs a single "Start full development environment" action. All required services (MongoDB, backend API, frontend app) start successfully and become ready for use. The developer sees clear feedback that the environment is starting and no error message appears.

**Why this priority**: This is the core value—enabling developers to begin work without manual steps or permission/configuration errors.

**Independent Test**: Run the Start full development environment task from the IDE; confirm MongoDB, backend, and frontend are running and reachable (e.g. backend health and frontend UI load). No permission-denied or "container not found" errors.

**Acceptance Scenarios**:

1. **Given** the developer has the project open in Cursor and the task is available, **When** they run "Start full development environment", **Then** all three components (MongoDB, backend, frontend) are started and the task completes without showing an error message.
2. **Given** no services are currently running, **When** the developer runs the start task, **Then** they can access the backend API and the frontend application within a reasonable time (e.g. under two minutes) without manual intervention.
3. **Given** the task has been run successfully, **When** the developer checks service status (or uses the app), **Then** MongoDB, backend, and frontend are all operational.

---

### User Story 2 - Task Configuration Aligned with Cursor (Priority: P2)

The start task and any related task definitions (stop, status, etc.) are stored in a single, valid configuration that Cursor can load. There are no duplicate or conflicting definitions, and no references to IDE-specific behavior that only worked in VSCode.

**Why this priority**: Prevents the "run task → error" experience and avoids confusion from multiple or broken task definitions.

**Independent Test**: Open the task configuration in the repo; confirm it is valid (e.g. single valid JSON where applicable) and that "Start full development environment" (or its label) exists once and points to the intended behavior. Run the task in Cursor and confirm it executes without configuration-related errors.

**Acceptance Scenarios**:

1. **Given** the project is opened in Cursor, **When** the developer opens the list of available tasks, **Then** "Start full development environment" appears once with a clear description.
2. **Given** `.vscode/tasks.json` exists in the project, **When** it is validated (syntax and structure), **Then** no duplicate or malformed definitions cause the start action to fail or behave inconsistently.
3. **Given** the project was originally set up for VSCode, **When** the audit is complete, **Then** any VSCode-only assumptions (e.g. how Docker or the shell is invoked) are documented and, where necessary, updated so the same task works in Cursor.

---

### User Story 3 - Clear Feedback and Optional Stop (Priority: P3)

When the developer runs the start task, they MUST receive explicit user-facing messages in the terminal (e.g. "Starting…" and "Ready" or "All services started") so progress and completion are clear. A "Stop full development environment" (or equivalent) task MUST be available so the developer can shut down all services from the IDE in one action.

**Why this priority**: Improves day-to-day experience and rounds out the workflow without being blocking for the core start behavior.

**Independent Test**: Run the start task and observe the terminal or task output for clear messages; run the stop task (if present) and confirm services stop.

**Acceptance Scenarios**:

1. **Given** the developer runs the start task, **When** the task runs, **Then** they see explicit user-facing messages (e.g. "Starting…", "All services started" or "Ready") in the terminal, not only raw command output or errors.
2. **Given** the developer has started the environment, **When** they run the "Stop full development environment" task, **Then** MongoDB, backend, and frontend are stopped and the task completes without error (with clear feedback where applicable).

---

### Edge Cases

- What happens when Docker is not installed or not running? The task should fail with a clear, actionable message (e.g. "Docker is not running" or "Start Docker and try again") rather than a generic permission or connection error where possible.
- What happens when required ports (e.g. for backend or frontend) are already in use? Behavior is documented or the task/message guides the user (e.g. stop existing process or use a different port).
- How does the system handle the case where the task is run from a context where the user does not have permission to start containers or processes? The failure is identifiable (e.g. permission denied) and documentation or messaging indicates the required permission or environment (e.g. user in Docker group, or run from a terminal where Docker is available).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The project MUST provide a single, runnable "Start full development environment" task that starts MongoDB, the backend service, and the frontend application. The task MUST use Docker Compose only (one command; all three services run as containers).
- **FR-002**: The start task MUST be executable from Cursor without modification by the developer (e.g. no manual sudo or path changes) when their environment (Docker, permissions, ports) is correctly set up.
- **FR-002b**: The start task MUST print explicit user-facing messages (e.g. "Starting…", "All services started" or "Ready") in the terminal so the developer sees clear progress and completion.
- **FR-003**: Task configuration MUST live in `.vscode/tasks.json` only, be valid and consumable by Cursor (e.g. no duplicate JSON blocks or invalid syntax that prevent the task from being listed or run).
- **FR-003b**: The canonical task labels MUST be "Start full development environment" and "Stop full development environment" (no emoji in the label); description/detail may include additional text or icons.
- **FR-004**: When the start task fails (e.g. Docker unavailable or permission denied), the outcome MUST be identifiable so the developer or documentation can direct the user to fix the environment (e.g. start Docker, add user to Docker group).
- **FR-005**: The audit MUST document what was changed from the original VSCode-oriented setup (if anything) and any assumptions about the environment (e.g. Docker installed, user in Docker group, ports 27017, 8000, 3001).
- **FR-006**: The project MUST provide a "Stop full development environment" (or equivalent) task that stops MongoDB, backend, and frontend in one action (e.g. via Docker Compose down).

### Key Entities

- **Start full development environment task**: The single IDE task with label "Start full development environment" (no emoji) that, when run, starts MongoDB, backend, and frontend via Docker Compose. It is defined in `.vscode/tasks.json` and must work in Cursor.
- **Stop full development environment task**: The IDE task with label "Stop full development environment" (no emoji) that stops MongoDB, backend, and frontend in one action (e.g. Docker Compose down). Defined in `.vscode/tasks.json`.
- **Task configuration**: The single file `.vscode/tasks.json` in the repository that defines IDE tasks (e.g. start, stop, status). Must be consistent, valid, and free of duplicates or VSCode-only assumptions that break Cursor.
- **Development environment**: The set of services (MongoDB, backend API, frontend app) required for local development, run as containers via Docker Compose, and their expected ports or endpoints.

## Assumptions

- The start task uses Docker Compose only: a single command (e.g. `docker compose up -d`) starts MongoDB, backend, and frontend as containers. No mixed mode (local uvicorn/npm) for this task.
- Cursor can run the same task format (e.g. shell tasks with a command and working directory) as VSCode; differences are limited to how the shell or Docker is invoked (e.g. permissions, default shell).
- Developers have or can get Docker and Docker Compose installed and their user in the Docker group (or equivalent) so that the start task does not require manual sudo for Docker commands.
- Success is measured by "task runs without error and all three services are running" via Docker Compose.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Developers can start the full development environment (MongoDB, backend, frontend) with one IDE action in under two minutes, without seeing an error message, when their environment is correctly set up.
- **SC-002**: The "Start full development environment" task appears exactly once in the task list and runs without configuration or syntax errors when executed in Cursor.
- **SC-003**: When the task fails due to environment issues (e.g. Docker not running, permission denied), the cause is identifiable from the task output or documentation so the developer can fix it without guessing.
- **SC-004**: An audit document or changelog describes what was updated from the original VSCode setup and what the project assumes about the developer’s environment (Docker, permissions, ports).
