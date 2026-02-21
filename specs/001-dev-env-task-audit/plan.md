# Implementation Plan: Development Environment Task Audit

**Branch**: `001-dev-env-task-audit` | **Date**: 2025-02-19 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `specs/001-dev-env-task-audit/spec.md`

**Architectural guidelines (must adhere)**:
- **Strict Containerization (Option A)**: All services in Docker Compose; docker-compose.yml configured for hot-reloading (volumes) where it keeps local development fluid.
- **Single Source of Truth**: All task definitions in `.vscode/tasks.json` only; identify and delete legacy startup scripts; remove redundant tasks.
- **Lifecycle Symmetry**: Start and Stop as a mandatory pair; use `docker compose up -d --wait` so services are ready before the task completes.
- **Deterministic Labels**: Exact labels "Start full development environment" and "Stop full development environment"; no emojis.
- **Readiness Feedback**: Explicit "Ready" messages in task output (e.g. `docker compose up -d --wait && echo "Environment is READY at ..."`).
- **Documentation Audit**: README/onboarding updated to state that Docker Compose via VS Code Tasks is the only supported way to run the environment.

---

## Summary

Consolidate development environment startup into a single, Cursor-compatible path: one canonical task configuration in `.vscode/tasks.json` with two tasks—**Start full development environment** and **Stop full development environment**—both using Docker Compose. Remove duplicate and legacy task definitions, remove or deprecate legacy shell/Python startup scripts that conflict with this model, add explicit readiness messaging, and update documentation so Docker Compose via VS Code Tasks is the only supported way to run the stack.

---

## Technical Context

**Language/Version**: Python 3.11 (backend), Node 20 (frontend); Docker Compose for orchestration.  
**Primary Dependencies**: FastAPI/uvicorn (backend), Next.js (frontend), MongoDB 4.4, Docker & Docker Compose.  
**Storage**: MongoDB (containers use docker-compose volume `mongodb_data`).  
**Testing**: pytest (backend), Next.js tooling (frontend); no change to test harness for this feature.  
**Target Platform**: Local development on Linux/macOS/WSL; Cursor and VS Code as IDEs.  
**Project Type**: Web application (backend at repo root, frontend in `frontend/`).  
**Performance Goals**: Start task completes within two minutes; services reachable (backend 8000, frontend 3001).  
**Constraints**: Single valid `.vscode/tasks.json`; no emoji in task labels; tasks must run without sudo when user is in Docker group.  
**Scale/Scope**: Single developer machine; three services (mongo, web, frontend).

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The project constitution (`.specify/memory/constitution.md`) is a template with placeholders only. No project-specific gates are defined. Proceeding per feature spec and the architectural guidelines above. No violations asserted.

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

docker-compose.yml       # Existing; ensure hot-reload volumes if needed for dev

# Legacy scripts to identify for removal/deprecation (see research.md):
scripts/
├── start_api.sh
├── start_app.sh
├── start_frontend.sh
├── start_api_server.sh
├── stop_app.sh
├── start_backend.py
├── start-complete.sh
├── start-dev.sh
├── quick-start.sh
├── start-with-correct-ports.sh
├── start-mongo-locally.sh
├── start-corporate.sh
├── start_fixed_*.sh
├── restart_*.sh
├── complete-restart.sh
└── ... (other startup/restart scripts)

frontend/
├── rebuild-and-start.sh # Candidate for removal or doc-only
└── ...
```

**Structure Decision**: Web app layout is unchanged. This feature only modifies `.vscode/tasks.json`, removes or deprecates scripts under `scripts/` that duplicate Docker Compose startup, and updates README/docs.

---

## Phase 0: Research & Decisions

See [research.md](./research.md) for:
- Use of `docker compose up -d --wait` and timeout behavior
- Exact readiness message and URLs (backend 8000, frontend 3001)
- List of legacy scripts to remove vs retain for reference
- Hot-reload volume strategy for docker-compose (if any)

---

## Phase 1: Design & Contracts

1. **Task configuration model** → [data-model.md](./data-model.md): structure of `.vscode/tasks.json`; only two tasks; canonical labels and command shapes.
2. **Task contract** → [contracts/task-definition.md](./contracts/task-definition.md): expected task labels, commands, and presentation options so implementations and tests can assert correctness.
3. **Quickstart** → [quickstart.md](./quickstart.md): run "Start full development environment" from IDE; open backend and frontend URLs; run "Stop full development environment" when done.

---

## Phase 2: Implementation Outline (for /speckit.tasks)

1. **Fix `.vscode/tasks.json`**
   - Replace entire file with a single valid JSON object.
   - Exactly two tasks: "Start full development environment", "Stop full development environment".
   - Start: `echo "Starting..." && docker compose up -d --wait && echo "Environment is READY. Backend: http://localhost:8000 | Frontend: http://localhost:3001"`
   - Stop: `echo "Stopping..." && docker compose down && echo "Environment stopped."`
   - `options.cwd`: `${workspaceFolder}`. No emoji in labels; `detail` may describe the task.

2. **Docker Compose**
   - Confirm `docker-compose.yml` starts mongo, web (backend), frontend.
   - If hot-reload is required for backend/frontend during dev, add volume mounts for source (e.g. `.` for backend, `frontend` for frontend) and ensure process uses --reload or equivalent inside the container; document in research.md/quickstart.

3. **Legacy scripts**
   - Remove or move to `scripts/legacy/` (or delete) all startup/restart scripts that duplicate "start backend + frontend + mongo" or "stop all" so the single source of truth is the VS Code task + Docker Compose. List in research.md.

4. **Documentation**
   - Update README (and any onboarding doc): state that the only supported way to run the full development environment is Docker Compose via the VS Code/Cursor task "Start full development environment". Remove or qualify instructions that say "run uvicorn..." or "run npm run dev" or "use script X" as the primary path. Document prerequisites: Docker, Docker Compose, user in Docker group; ports 8000, 3001, 27017.

5. **Audit changelog**
   - Add a short audit note (in README or `specs/001-dev-env-task-audit/CHANGELOG.md`) describing what was changed from the previous VSCode-oriented setup (single tasks file, Docker Compose only, legacy scripts removed/deprecated, docs updated).

---

## Complexity Tracking

No constitution violations. This section is empty.
