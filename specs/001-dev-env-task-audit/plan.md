# Implementation Plan: Development Environment Task Audit

**Branch**: `001-dev-env-task-audit` | **Date**: 2025-02-19 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `specs/001-dev-env-task-audit/spec.md`

**Architectural guidelines (must adhere)**:
- **Strict Containerization**: All services in Docker Compose; compose file at repo root `docker-compose.yml` only; use Docker Compose V2 CLI (`docker compose`), not legacy `docker-compose`.
- **Single Source of Truth**: All task definitions in `.vscode/tasks.json` only; identify and deprecate/remove legacy startup scripts; remove redundant tasks.
- **Lifecycle Symmetry**: Start and Stop as a mandatory pair. Task completes only after backend and/or frontend respond to a health check (or defined wait)—not only when `docker compose up -d` returns. Use `docker compose up -d --wait` so Compose healthchecks are satisfied before task success.
- **Deterministic Labels**: Exact labels "Start full development environment" and "Stop full development environment"; no emojis.
- **Readiness Feedback**: Explicit user-facing messages: "Starting…", "All services started" or "Ready", plus backend/frontend URLs. When services are already running, succeed with a short message (e.g. "Services already running").
- **Port & Failure Behavior**: Backend port 8088, frontend 3001, MongoDB 27017 (per project constitution). When ports are in use, fail with a clear, actionable message; do not automatically stop other processes.
- **Documentation Audit**: README/onboarding updated to state that Docker Compose via VS Code/Cursor tasks is the only supported way to run the environment.

---

## Summary

Consolidate development environment startup into a single, Cursor-compatible path: one canonical task configuration in `.vscode/tasks.json` with two tasks—**Start full development environment** and **Stop full development environment**—both using Docker Compose V2 and repo-root `docker-compose.yml`. Start task completes only after health check (or equivalent); already-running case shows a short success message; port conflict fails with a clear message. Remove or deprecate legacy startup scripts, add explicit readiness messaging, and update documentation so Docker Compose via VS Code/Cursor tasks is the only supported way to run the stack.

---

## Technical Context

**Language/Version**: Python 3.11 (backend), Node 20 (frontend); Docker Compose V2 for orchestration.  
**Primary Dependencies**: FastAPI/uvicorn (backend), Next.js (frontend), MongoDB 4.4, Docker & Docker Compose V2 plugin.  
**Storage**: MongoDB (containers use docker-compose volume `mongodb_data`).  
**Testing**: pytest (backend), Next.js tooling (frontend); no change to test harness for this feature.  
**Target Platform**: Local development on Linux/macOS/WSL; Cursor and VS Code as IDEs.  
**Project Type**: Web application (backend at repo root, frontend in `frontend/`).  
**Performance Goals**: Start task completes within two minutes; services reachable (backend 8088, frontend 3001 per constitution).  
**Constraints**: Single valid `.vscode/tasks.json`; no emoji in task labels; tasks must run without sudo when user is in Docker group; Compose file at repo root `docker-compose.yml`; Docker Compose V2 CLI only; task success only after health check (or equivalent wait).  
**Scale/Scope**: Single developer machine; three services (mongo, web, frontend).

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Backend port 8088, Frontend 3001, MongoDB 27017** (spec/constitution/project-constitution.speckit.md): Plan and task output URLs use backend 8088; if docker-compose currently exposes backend on 8000, implementation must align to 8088 or document exception.
- **No project root files**: This feature only modifies `.vscode/tasks.json`, repo-root `docker-compose.yml`, and docs/scripts; no new files at project root.
- No other constitution gates apply. Proceeding per feature spec and the architectural guidelines above.

---

## Project Structure

### Documentation (this feature)

```text
specs/001-dev-env-task-audit/
├── plan.md              # This file
├── research.md          # Phase 0: decisions and rationale
├── data-model.md        # Phase 1: task config structure
├── quickstart.md        # Phase 1: how to run the environment
├── contracts/           # Phase 1: task contract (expected labels/commands)
└── tasks.md             # Phase 2: /speckit.tasks output (not created by plan)
```

### Source Code (repository root)

```text
.vscode/
└── tasks.json           # Single file; only Start + Stop tasks (canonical labels)

docker-compose.yml       # Repo root; ensure backend exposed on 8088; healthchecks for web + frontend

# Legacy scripts to identify for removal/deprecation (see research.md):
scripts/
├── start_api.sh, start_app.sh, start_frontend.sh, start_api_server.sh
├── stop_app.sh, start_backend.py, start-complete.sh, start-dev.sh
├── quick-start.sh, start-with-correct-ports.sh, start-mongo-locally.sh
├── start-corporate.sh, start_fixed_*.sh, restart_*.sh, complete-restart.sh
└── ...

frontend/
├── rebuild-and-start.sh # Candidate for removal or doc-only
└── ...
```

**Structure Decision**: Web app layout is unchanged. This feature only modifies `.vscode/tasks.json`, aligns docker-compose (ports/healthchecks), removes or deprecates scripts under `scripts/` that duplicate Docker Compose startup, and updates README/docs.

---

## Phase 0: Research & Decisions

See [research.md](./research.md) for:
- Docker Compose V2 only; `docker compose up -d --wait` and healthcheck behavior
- Exact readiness message and URLs (backend 8088, frontend 3001)
- Already-running: succeed with "Services already running" (or equivalent)
- Port conflict: fail with clear, actionable message; no auto-stop
- List of legacy scripts to remove vs retain for reference
- Hot-reload volume strategy for docker-compose (if any)

---

## Phase 1: Design & Contracts

1. **Task configuration model** → [data-model.md](./data-model.md): structure of `.vscode/tasks.json`; only two tasks; canonical labels and command shapes; Compose V2, repo root, health-check completion.
2. **Task contract** → [contracts/task-definition.md](./contracts/task-definition.md): expected task labels, commands, backend 8088 / frontend 3001, and presentation options so implementations and tests can assert correctness.
3. **Quickstart** → [quickstart.md](./quickstart.md): run "Start full development environment" from IDE; open backend (8088) and frontend (3001) URLs; run "Stop full development environment" when done; troubleshooting (Docker, port conflict, already running).

---

## Phase 2: Implementation Outline (for /speckit.tasks)

1. **Fix `.vscode/tasks.json`**
   - Replace entire file with a single valid JSON object.
   - Exactly two tasks: "Start full development environment", "Stop full development environment".
   - Use Docker Compose V2 only: `docker compose` (not `docker-compose`). Working directory: repo root (`options.cwd`: `${workspaceFolder}`); compose file is repo root `docker-compose.yml`.
   - Start command: (1) Print "Starting…"; (2) Run `docker compose up -d --wait` (task completes only after Compose healthchecks pass); (3) When already running, succeed and print "Services already running" or "All services are already up" (idempotent behavior); (4) On success, print "Environment is READY" with backend http://localhost:8088 and frontend http://localhost:3001. Avoid platform-only wrappers (e.g. `sg docker`) that break on macOS/Windows; document Linux Docker group in quickstart.
   - Stop: `echo "Stopping..." && docker compose down && echo "Environment stopped."`
   - Port conflict: when ports 27017, 8088, or 3001 are in use, fail with a clear, actionable message (which port, what to do); do not automatically stop other processes. Implement via small script or inline check; document in research.md.
   - No emoji in labels; `detail` may describe the task.

2. **Docker Compose**
   - Compose file: repo root `docker-compose.yml` only; tasks run with cwd = workspace root. Use Docker Compose V2 CLI.
   - Ensure `docker-compose.yml` starts mongo, web (backend), frontend; backend MUST be exposed on host port 8088 (constitution). If current compose uses 8000, change to 8088 (e.g. `"8088:8000"` if app listens on 8000 inside container).
   - Start task MUST complete only after backend and/or frontend pass health check: use `docker compose up -d --wait`; ensure docker-compose.yml has healthchecks for web and frontend.
   - If hot-reload is required for dev, add volume mounts and document in research/quickstart.

3. **Legacy scripts**
   - Remove or move to `scripts/legacy/` (or delete) all startup/restart scripts that duplicate "start backend + frontend + mongo" or "stop all" so the single source of truth is the VS Code task + Docker Compose. List in research.md.

4. **Documentation**
   - Update README (and any onboarding doc): only supported way to run the full development environment is Docker Compose via the VS Code/Cursor task "Start full development environment". Remove or qualify "run uvicorn" / "npm run dev" / "use script X" as primary path. Document prerequisites: Docker, Docker Compose V2, user in Docker group; ports 8088 (backend), 3001 (frontend), 27017 (MongoDB). Document port conflict: fail with clear message; do not auto-stop other processes.

5. **Audit changelog**
   - Add a short audit note (README or `specs/001-dev-env-task-audit/CHANGELOG.md`) describing what was changed from the previous VSCode-oriented setup (single tasks file, Docker Compose V2 only, repo root compose, health-check completion, already-running message, port conflict handling, legacy scripts removed/deprecated, docs updated).

---

## Complexity Tracking

No constitution violations. This section is empty.
