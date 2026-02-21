# Tasks: Development Environment Task Audit

**Feature**: 001-dev-env-task-audit  
**Input**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [contracts/task-definition.md](./contracts/task-definition.md)  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story (US1, US2, US3) and polish. No optional test tasks (spec does not require new automated tests).

---

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: US1, US2, US3 for traceability to spec user stories
- Paths: `.vscode/tasks.json`, `scripts/`, `README.md`, `docker-compose.yml` at repository root

---

## Phase 1: Setup (Shared)

**Purpose**: Prepare for single source of truth (legacy script handling).

- [x] **T001** [P] Create `scripts/legacy/` directory and add `scripts/legacy/README.md` stating that scripts in this folder are deprecated; the only supported way to start/stop the full environment is the VS Code/Cursor task "Start full development environment" / "Stop full development environment" using Docker Compose. (Skip if scripts will be deleted instead of moved.)

---

## Phase 2: User Story 1 – One-Click Start of Full Stack (P1)

**Goal**: One IDE action starts MongoDB, backend, and frontend via Docker Compose with clear feedback.  
**Independent Test**: Run "Start full development environment" from Cursor; confirm backend (8000) and frontend (3001) are reachable and readiness message appears.

- [x] **T002** [US1] Replace the entire contents of `.vscode/tasks.json` with a **single valid JSON object** (no concatenated blocks). Include exactly two tasks:
  - **Task 1** – `label`: `"Start full development environment"` (no emoji). `type`: `"shell"`. `command`: `echo "Starting..." && docker compose up -d --wait && echo "Environment is READY. Backend: http://localhost:8000 | Frontend: http://localhost:3001"`. `options.cwd`: `"${workspaceFolder}"`. Add `detail` and `presentation` as needed (see [contracts/task-definition.md](./contracts/task-definition.md)).
  - **Task 2** – `label`: `"Stop full development environment"` (no emoji). `type`: `"shell"`. `command`: `echo "Stopping..." && docker compose down && echo "Environment stopped."`. `options.cwd`: `"${workspaceFolder}"`.
- [x] **T003** [US1] Verify in Cursor: Run "Start full development environment"; confirm task exits with code 0, terminal shows "Starting..." and "Environment is READY" with URLs; confirm http://localhost:8000 and http://localhost:3001 are reachable and MongoDB is running (e.g. `docker ps` shows mongo, web, frontend).

---

## Phase 3: User Story 2 – Task Configuration Aligned with Cursor (P2)

**Goal**: Single valid `.vscode/tasks.json`; no duplicate or conflicting definitions; no legacy tasks that reference local uvicorn/npm or emoji labels.  
**Independent Test**: Open `.vscode/tasks.json`; validate JSON (one root object); confirm only "Start full development environment" and "Stop full development environment" exist; run Start in Cursor without config errors.

- [x] **T004** [US2] Ensure `.vscode/tasks.json` contains **no second JSON object** and no tasks with emoji labels (e.g. "🚀 Start Full Development Environment", "🗄️ Start MongoDB", "🛑 Stop All Services"). If T002 replaced the file entirely, this is already done; otherwise remove the duplicate block and all non-canonical tasks so only the two tasks from T002 remain. Validate with a JSON linter or parser.
- [x] **T005** [US2] Remove or relocate legacy startup/stop scripts so they are not the primary path. Per [research.md](./research.md): either **delete** or **move to `scripts/legacy/`** the scripts that duplicate full-stack start/stop (e.g. `scripts/start_api.sh`, `scripts/start_app.sh`, `scripts/start_frontend.sh`, `scripts/start_api_server.sh`, `scripts/stop_app.sh`, `scripts/start_backend.py`, `scripts/start-complete.sh`, `scripts/start-dev.sh`, `scripts/quick-start.sh`, `scripts/start-with-correct-ports.sh`, `scripts/start-mongo-locally.sh`, `scripts/start-corporate.sh`, `scripts/start_fixed_*.sh`, `scripts/restart_*.sh`, `scripts/complete-restart.sh`, `frontend/rebuild-and-start.sh`). If moved, ensure `scripts/legacy/README.md` (from T001) explains they are unsupported.

---

## Phase 4: User Story 3 – Clear Feedback and Stop (P3)

**Goal**: Explicit user-facing messages for Start and Stop; Stop task stops all services with clear feedback.  
**Independent Test**: Run Start and confirm "Starting..." and "Environment is READY" in output; run Stop and confirm "Stopping..." and "Environment stopped." and containers are down.

- [x] **T006** [US3] Confirm Start task output includes explicit messages: "Starting..." before compose and "Environment is READY. Backend: http://localhost:8000 | Frontend: http://localhost:3001" after success (already specified in T002; verify in IDE).
- [x] **T007** [US3] Run "Stop full development environment" after a successful Start; confirm terminal shows "Stopping..." and "Environment stopped." and `docker compose ps` (or `docker ps`) shows no project containers running.

---

## Phase 5: Polish & Documentation

**Purpose**: Docker Compose sanity check, README as single source of truth, audit trail.

- [x] **T008** [P] Confirm `docker-compose.yml` at repo root defines services `mongo`, `web`, and `frontend` and exposes backend on 8000 and frontend on 3001. If hot-reload is desired for local dev, add a short note in [research.md](./research.md) or [quickstart.md](./quickstart.md) that volume mounts can be added later; no implementation required in this feature unless specified.
- [x] **T009** [P] Update **README.md**: (1) State that the **only supported way** to run the full development environment is **Docker Compose via the VS Code/Cursor task "Start full development environment"**. (2) Remove or qualify any instructions that say "run uvicorn...", "run npm run dev", or "use script X" as the primary way to start the stack. (3) Document prerequisites: Docker and Docker Compose installed, user in Docker group (so `docker` works without sudo); ports 8000 (backend), 3001 (frontend), 27017 (MongoDB). (4) Point to [specs/001-dev-env-task-audit/quickstart.md](./quickstart.md) for steps.
- [x] **T010** Add an **audit changelog**: In README (new section) or in `specs/001-dev-env-task-audit/CHANGELOG.md`, describe what was changed from the previous VSCode-oriented setup: single valid `.vscode/tasks.json` with two canonical tasks (Start, Stop); Docker Compose only; legacy startup/stop scripts removed or moved to `scripts/legacy/`; README updated so Docker Compose via VS Code Tasks is the only supported path.

---

## Dependencies & Execution Order

| Phase | Depends on | Notes |
|-------|------------|--------|
| Phase 1 (Setup) | None | T001 optional if deleting scripts |
| Phase 2 (US1) | Phase 1 | T002–T003 deliver one-click start |
| Phase 3 (US2) | Phase 2 | T004–T005 remove duplicates and legacy scripts |
| Phase 4 (US3) | Phase 2 | T006–T007 verify feedback and stop (can run after T003) |
| Phase 5 (Polish) | Phase 2 | T008–T010 can run after T002; T009–T010 after T005 if README references scripts |

**Suggested order**: T001 (optional) → T002 → T003 → T004 → T005 → T006 → T007 → T008, T009, T010.

---

## Parallel Opportunities

- **T001** and **T002** can be done in parallel (different files).
- **T008**, **T009**, **T010** can be done in parallel after the core task file and scripts are updated.

---

## Implementation Notes

- Use `docker compose up -d --wait` for Start; if the environment does not support `--wait`, use `docker compose up -d` and document in quickstart that "Ready" means containers started (consider a short sleep or health-check poll in the task if needed).
- Keep task labels **exactly** "Start full development environment" and "Stop full development environment" (no emoji) for script and AI stability per architectural guidelines.
- After T002, run the Start task once in Cursor to confirm no permission or "command not found" errors when Docker is available and user is in the Docker group.
