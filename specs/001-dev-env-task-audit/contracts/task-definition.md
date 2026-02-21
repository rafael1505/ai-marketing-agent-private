# Contract: Development Environment Tasks

**Feature**: 001-dev-env-task-audit  
**Purpose**: Define the expected shape of the two canonical IDE tasks so implementations and tests can assert correctness.

---

## File contract

- **Location**: `.vscode/tasks.json`
- **Schema**: VS Code Tasks 2.0 (single root object; `version`, `tasks`).
- **Content**: Exactly two tasks; no duplicate or concatenated JSON.

---

## Task 1: Start full development environment

| Field | Requirement |
|-------|-------------|
| `label` | Exactly `Start full development environment` (no emoji) |
| `type` | `shell` |
| `command` | Must (1) start all services via Docker Compose, (2) wait for readiness when possible (`docker compose up -d --wait` or equivalent), (3) print explicit user-facing messages including a "Ready" or "READY" line with backend and frontend URLs |
| `options.cwd` | `"${workspaceFolder}"` |

**Acceptance**: Running this task from the IDE results in exit code 0 and terminal output containing a readiness message (e.g. "Environment is READY") and URLs for backend (port 8000) and frontend (port 3001). After the task completes, http://localhost:8000 and http://localhost:3001 are reachable.

---

## Task 2: Stop full development environment

| Field | Requirement |
|-------|-------------|
| `label` | Exactly `Stop full development environment` (no emoji) |
| `type` | `shell` |
| `command` | Must stop all services (e.g. `docker compose down`) and print clear feedback |
| `options.cwd` | `"${workspaceFolder}"` |

**Acceptance**: Running this task after Start results in exit code 0 and terminal output indicating services are stopped. Containers for the project's compose stack are no longer running.

---

## Out of scope

- Other tasks (e.g. status check, restart) are not part of this contract; they may be added later without changing the two canonical labels above.
- Implementation details of Docker Compose (e.g. service names, healthchecks) are not part of this task contract.
