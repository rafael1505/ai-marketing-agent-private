# Tasks: Development Environment Task Audit

**Feature**: 001-dev-env-task-audit  
**Generated from**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [contracts/task-definition.md](./contracts/task-definition.md)  
**Last updated**: 2026-02-19  
**Status**: ✅ All tasks completed  

---

## Task Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel with other tagged tasks (touches different files, no dependency)
- **[Story]**: US1–US3 for traceability; P = Polish/cross-cutting
- All file paths are relative to repo root

---

## Phase 1: Setup (Shared Baseline)

**Purpose**: Create the legacy scripts container and align Docker Compose to constitutional ports before touching the IDE task.

---

### T001 [P] Create `scripts/legacy/` and deprecation README

**Story**: P  
**Estimated time**: 15 min  
**Files**: `scripts/legacy/README.md` (create)

**Steps**:
1. [x] Create directory `scripts/legacy/`
2. [x] Create `scripts/legacy/README.md` with content:
   ```
   # Legacy Scripts (Deprecated)

   Scripts in this folder are no longer supported.
   The only supported way to start or stop the full development environment is:

     VS Code / Cursor task: "Start full development environment"
     VS Code / Cursor task: "Stop full development environment"

   These tasks use Docker Compose V2 (docker compose up/down) with the
   repo-root docker-compose.yml file.

   Scripts here are kept for historical reference only.
   ```

**Acceptance criteria**:
- `scripts/legacy/` exists
- `scripts/legacy/README.md` clearly marks scripts as unsupported and points to the canonical tasks

---

### T002 [P] Align `docker-compose.yml` backend port to 8088

**Story**: P  
**Estimated time**: 15 min  
**Files**: `docker-compose.yml`

**Steps**:
1. [x] Open `docker-compose.yml` at repo root
2. [x] Find the `web` (backend) service's `ports` mapping — currently `"8000:8000"`
3. [x] Change the host port to 8088: `"8088:8000"` (host 8088 → container 8000, since the backend listens on 8000 inside the container)
4. [x] Confirm `frontend` service still exposes `"3001:3001"` and `mongo` still exposes `"27017:27017"`
5. [x] Confirm `web` service still has a `healthcheck` targeting `http://localhost:8000` inside the container (internal URL; the external port is 8088)
6. [x] Confirm `frontend` service still has a `healthcheck`

**Acceptance criteria**:
- `docker-compose.yml` exposes backend on host port **8088** (matching project constitution)
- Frontend on **3001**, MongoDB on **27017** — unchanged
- Healthchecks present for `mongo`, `web`, and `frontend` services (required for `--wait` to be meaningful)
- `docker compose config` reports no syntax errors

---

## Phase 2: User Story 1 – One-Click Start of Full Stack

**Goal**: One IDE action starts MongoDB, backend, and frontend via Docker Compose V2; task completes only after health checks pass; explicit messages shown.  
**Independent Test**: Run "Start full development environment" in Cursor; backend at http://localhost:8088 and frontend at http://localhost:3001 are reachable; terminal shows readiness message.

---

### T003 [US1] Replace `.vscode/tasks.json` with canonical two-task config

**Story**: US1  
**Estimated time**: 20 min  
**Files**: `.vscode/tasks.json`  
**Depends on**: T002

**Steps**:
1. [x] Replace the **entire contents** of `.vscode/tasks.json` with the following single valid JSON object:
   ```json
   {
     "version": "2.0.0",
     "tasks": [
       {
         "label": "Start full development environment",
         "type": "shell",
         "command": "echo 'Starting...' && docker compose up -d --wait && echo 'Environment is READY. Backend: http://localhost:8088 | Frontend: http://localhost:3001'",
         "options": {
           "cwd": "${workspaceFolder}"
         },
         "problemMatcher": [],
         "detail": "Starts MongoDB, backend (port 8088), and frontend (port 3001) via Docker Compose V2. Waits for services to be healthy. Requires Docker and user in docker group.",
         "presentation": {
           "echo": true,
           "reveal": "always",
           "focus": true,
           "panel": "shared"
         }
       },
       {
         "label": "Stop full development environment",
         "type": "shell",
         "command": "echo 'Stopping...' && docker compose down && echo 'Environment stopped.'",
         "options": {
           "cwd": "${workspaceFolder}"
         },
         "problemMatcher": [],
         "detail": "Stops all services (MongoDB, backend, frontend) via Docker Compose V2.",
         "presentation": {
           "echo": true,
           "reveal": "always",
           "focus": true,
           "panel": "shared"
         }
       }
     ]
   }
   ```
2. [x] Validate the file is valid JSON (one root object, no concatenated blocks): `python3 -m json.tool .vscode/tasks.json`
3. [x] Confirm:
   - Labels are exactly `"Start full development environment"` and `"Stop full development environment"` — no emoji, no extra whitespace
   - Both tasks use `docker compose` (space, V2 CLI) — not `docker-compose`
   - `options.cwd` is `"${workspaceFolder}"` (repo root where `docker-compose.yml` lives)
   - No `sg docker` wrapper or other platform-specific wrappers

**Acceptance criteria**:
- `.vscode/tasks.json` is a single valid JSON object
- Exactly two tasks with canonical labels
- Start command uses `docker compose up -d --wait` (health-check completion)
- URLs in readiness message use **8088** (backend) and **3001** (frontend)
- `python3 -m json.tool .vscode/tasks.json` exits 0

---

### T004 [US1] Handle already-running case

**Story**: US1  
**Estimated time**: 20 min  
**Files**: `.vscode/tasks.json`, optionally `scripts/start-dev-env.sh` (new helper)

**Steps**:
1. [x] Decide: use inline shell detection or a small helper script
2. [x] **Option A – Inline** (recommended for simplicity): Update the Start command to detect if services are already running and print a message:
   ```bash
   echo 'Starting...' && \
   if docker compose ps --services --filter status=running 2>/dev/null | grep -q .; then \
     echo 'Services already running. All services are already up.'; \
   else \
     docker compose up -d --wait && echo 'Environment is READY. Backend: http://localhost:8088 | Frontend: http://localhost:3001'; \
   fi
   ```
   Update the `command` value in `.vscode/tasks.json` accordingly.
3. [x] Re-validate JSON after edit: `python3 -m json.tool .vscode/tasks.json`

**Acceptance criteria**:
- Running Start when services are already up exits with code 0
- Terminal shows a short message (e.g. "Services already running. All services are already up.")
- Running Start when services are down still starts them and shows "Environment is READY"

---

### T005 [US1] Handle port-conflict case

**Story**: US1  
**Estimated time**: 30 min  
**Files**: `.vscode/tasks.json`

**Steps**:
1. [x] Update the Start command to check required ports (27017, 8088, 3001) before running compose up. Example inline check to prepend to the command:
   ```bash
   for PORT in 27017 8088 3001; do \
     if lsof -i:$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then \
       echo "ERROR: Port $PORT is already in use by another process. Stop that process before starting the development environment."; \
       exit 1; \
     fi; \
   done
   ```
2. [x] Combine with the already-running check from T004 so the order is: port check → already-running check → compose up
3. [x] Re-validate JSON: `python3 -m json.tool .vscode/tasks.json`
4. [x] **Document** in [quickstart.md](./quickstart.md) (already done in Phase 1 of plan): "When a required port is in use, the task fails with a clear message. Stop the process using that port. The task does not automatically stop other processes."

**Note**: `lsof` is standard on Linux/macOS/WSL. If not available, the port check gracefully skips and Docker Compose reports its own error; document this in quickstart.

**Acceptance criteria**:
- When port 8088 (or 3001 or 27017) is in use by a non-project process, the task fails with a message identifying which port and what to do
- Task exits non-zero on port conflict
- Task does NOT automatically kill or stop other processes
- `python3 -m json.tool .vscode/tasks.json` exits 0

---

### T006 [US1] Verify Start task end-to-end in Cursor

**Story**: US1  
**Estimated time**: 10 min  
**Files**: None (verification only)  
**Depends on**: T002, T003, T004, T005

**Steps**:
1. [x] Open Cursor with project at repo root
2. [x] Run "Start full development environment" via Command Palette → Tasks: Run Task
3. [x] Confirm terminal shows:
   - `Starting...`
   - (compose output)
   - `Environment is READY. Backend: http://localhost:8088 | Frontend: http://localhost:3001`
4. [x] Confirm http://localhost:8088/api/v1/diagnostic/health (or `/docs`) returns a valid response
5. [x] Confirm http://localhost:3001 loads the frontend
6. [x] Run `docker ps` — confirm `mongo`, `web`, `frontend` containers are running
7. [x] Run Start again (services already up) — confirm it exits 0 with "already running" message
8. [x] Task exit code is 0

**Acceptance criteria**:
- SC-001: Full environment starts in < 2 min, task exit code 0, both URLs reachable
- SC-002: Task appears once in task list, no config errors
- Already-running: task succeeds with short message (not an error)

---

## Phase 3: User Story 2 – Task Config Aligned with Cursor

**Goal**: Single valid `.vscode/tasks.json`; no duplicates; no legacy/emoji tasks; no VSCode-only assumptions.  
**Independent Test**: Validate JSON structure; confirm only two canonical tasks exist; run in Cursor without config errors.

---

### T007 [US2] Remove duplicate/legacy/emoji tasks from `.vscode/tasks.json`

**Story**: US2  
**Estimated time**: 10 min  
**Files**: `.vscode/tasks.json`  
**Depends on**: T003 (T003 already replaces the file entirely; this task is a verification step)

**Steps**:
1. [x] Open `.vscode/tasks.json`
2. [x] Confirm there is **exactly one root JSON object** (no second `{...}` block concatenated after the first)
3. [x] Confirm the `tasks` array has **exactly 2 entries** — no tasks with emoji labels (🚀, 🗄️, 🛑, etc.), no "Start MongoDB only", no "Check Services Status", no mixed local/Docker tasks
4. [x] If any extra tasks remain, remove them so only the two canonical tasks exist
5. [x] Re-validate: `python3 -m json.tool .vscode/tasks.json`

**Acceptance criteria**:
- `tasks` array has exactly 2 entries with canonical labels
- No emoji in any task `label`
- File is valid JSON
- No VSCode-only assumptions (e.g. `sg docker` wrapper removed)

---

### T008 [P][US2] Move legacy startup/stop scripts to `scripts/legacy/`

**Story**: US2  
**Estimated time**: 20 min  
**Files**: `scripts/`, `frontend/`  
**Depends on**: T001

**Steps**:
1. [x] Move (or delete) the following scripts to `scripts/legacy/` (per [research.md](./research.md)):
   - `scripts/start_api.sh`
   - `scripts/start_app.sh`
   - `scripts/start_frontend.sh`
   - `scripts/start_api_server.sh`
   - `scripts/stop_app.sh`
   - `scripts/start_backend.py`
   - `scripts/start-complete.sh`
   - `scripts/start-dev.sh`
   - `scripts/quick-start.sh`
   - `scripts/start-with-correct-ports.sh`
   - `scripts/start-mongo-locally.sh`
   - `scripts/start-corporate.sh` (or keep with a note for proxy environments)
   - `scripts/start_fixed_*.sh`, `scripts/restart_*.sh`, `scripts/complete-restart.sh`
   - `frontend/rebuild-and-start.sh`
2. [x] Keep scripts only used by CI/tests (e.g. integration test runners that start uvicorn internally) — those are out of scope
3. [x] Confirm `scripts/legacy/README.md` (from T001) is in place

**Acceptance criteria**:
- No startup/stop scripts remain in `scripts/` root or `frontend/` that duplicate the Docker Compose task
- All moved scripts are in `scripts/legacy/`
- `scripts/legacy/README.md` marks them as unsupported

---

## Phase 4: User Story 3 – Clear Feedback and Stop

**Goal**: Explicit messages for Start and Stop; Stop task shuts down all services cleanly.  
**Independent Test**: Run Start → see "Starting…" + "READY" message; run Stop → see "Stopping…" + "stopped" + containers down.

---

### T009 [US3] Verify Stop task end-to-end

**Story**: US3  
**Estimated time**: 10 min  
**Files**: None (verification only)  
**Depends on**: T006

**Steps**:
1. [x] After T006 (services running), run "Stop full development environment" via Tasks: Run Task
2. [x] Confirm terminal shows:
   - `Stopping...`
   - (compose down output)
   - `Environment stopped.`
3. [x] Confirm `docker compose ps` shows no running project containers
4. [x] Task exit code is 0

**Acceptance criteria**:
- Stop task exits 0 with clear messages
- All containers stopped after task completes

---

## Phase 5: Polish & Documentation

**Purpose**: Docker Compose sanity check, README as single source of truth, audit trail.

---

### T010 [P] Verify `docker-compose.yml` healthchecks and services

**Story**: P  
**Estimated time**: 10 min  
**Files**: `docker-compose.yml`  
**Depends on**: T002

**Steps**:
1. [x] Confirm services `mongo`, `web`, `frontend` are all defined
2. [x] Confirm `web` healthcheck targets `http://localhost:8000/api/v1/diagnostic/health` (inside container; external is 8088)
3. [x] Confirm `frontend` healthcheck targets `http://127.0.0.1:3001` (inside container)
4. [x] Confirm `mongo` healthcheck uses `mongo --eval "db.adminCommand('ping')"`
5. [x] Run `docker compose config` — exits 0, no warnings

**Acceptance criteria**:
- All three services have healthchecks
- Backend exposed on host port 8088 (from T002)
- `docker compose config` exits 0

---

### T011 [P] Update README with Docker Compose as only supported start path

**Story**: P  
**Estimated time**: 30 min  
**Files**: `README.md`  
**Depends on**: T003, T008

**Steps**:
1. [x] Update "Getting Started" / "Development Setup" section:
   - State: **The only supported way to run the full development environment is via the VS Code/Cursor task "Start full development environment"**.
   - Remove or qualify any instructions that say "run uvicorn...", "npm run dev", or "use script X" as the primary start path.
2. [x] Add/update **Prerequisites** section:
   - Docker (with Docker Compose V2 plugin — `docker compose`, not `docker-compose`)
   - User in the `docker` group (Linux/WSL): `sudo usermod -aG docker $USER` then log out/in
   - Ports 8088 (backend), 3001 (frontend), 27017 (MongoDB) must be free
3. [x] Add/update **Quick Start** section:
   - Command Palette → "Tasks: Run Task" → "Start full development environment"
   - Wait for: `Environment is READY. Backend: http://localhost:8088 | Frontend: http://localhost:3001`
   - Point to `specs/001-dev-env-task-audit/quickstart.md` for details and troubleshooting
4. [x] Add **Stopping** section:
   - Command Palette → "Tasks: Run Task" → "Stop full development environment"

**Acceptance criteria**:
- README states Docker Compose via IDE task is the only supported path
- Prerequisites list Docker Compose V2, Docker group, ports 8088/3001/27017
- No primary instructions for `uvicorn` / `npm run dev` / legacy scripts remain
- Quickstart link present

---

### T012 [P] Add audit changelog

**Story**: P  
**Estimated time**: 15 min  
**Files**: `specs/001-dev-env-task-audit/CHANGELOG.md`  
**Depends on**: T003, T008, T011

**Steps**:
1. [x] Update (or confirm content of) `specs/001-dev-env-task-audit/CHANGELOG.md` with an entry covering:
   - `.vscode/tasks.json`: replaced with single valid JSON; two canonical tasks (Start, Stop); Compose V2 CLI; no emoji; health-check completion via `--wait`
   - **Ports aligned to constitution**: backend now on host port 8088 (was 8000)
   - **Already-running behavior**: task succeeds with "Services already running" message
   - **Port-conflict behavior**: task fails with clear message; no auto-stop
   - **Legacy scripts**: moved to `scripts/legacy/` and marked unsupported
   - **README**: updated to Docker Compose via VS Code/Cursor task as only supported path; prerequisites updated

**Acceptance criteria**:
- CHANGELOG describes all changes made in this feature
- Port change (8000 → 8088) is documented
- All spec requirements (FR-001–FR-008, SC-001–SC-004) can be traced to at least one task

---

## Dependency & Execution Order

| Phase | Tasks | Depends on | Notes |
|-------|-------|------------|-------|
| Phase 1 – Setup | T001, T002 | — | Can run in parallel |
| Phase 2 – US1 | T003 | T002 | Replace tasks.json; must have correct port first |
| Phase 2 – US1 | T004, T005 | T003 | Extend command; run in sequence |
| Phase 2 – US1 | T006 | T002–T005 | End-to-end verification |
| Phase 3 – US2 | T007 | T003 | Verify/clean tasks.json |
| Phase 3 – US2 | T008 | T001 | Move legacy scripts |
| Phase 4 – US3 | T009 | T006 | Verify Stop |
| Phase 5 – Polish | T010 | T002 | Compose verification |
| Phase 5 – Polish | T011 | T003, T008 | README update |
| Phase 5 – Polish | T012 | T003, T008, T011 | Changelog |

**Recommended execution order**:  
`T001 + T002` (parallel) → `T003` → `T004` → `T005` → `T006` → `T007 + T008` (parallel) → `T009` → `T010 + T011` (parallel) → `T012`

---

## Parallel Opportunities

- **T001** and **T002** — different files, no dependency
- **T007** and **T008** — after T003/T001 respectively; different files
- **T010** and **T011** — after T002/T003 respectively; different files

---

## Spec Requirements Coverage

| Requirement | Covered by |
|-------------|-----------|
| FR-001: Docker Compose V2 only; health-check completion | T002, T003, T006 |
| FR-002: Runs without sudo when user in docker group | T003 (no `sg docker`), T011 (docs) |
| FR-002b: Explicit user-facing messages | T003 (Starting, READY), T009 (Stopping, stopped) |
| FR-003: `.vscode/tasks.json` only; valid; no duplicates | T003, T007 |
| FR-003b: Canonical labels, no emoji | T003, T007 |
| FR-004: Identifiable failure (Docker unavailable, permissions) | T003 (compose error surfaced), T011 (docs) |
| FR-005: Audit document | T012 |
| FR-006: Stop task required | T003, T009 |
| FR-007: Already running → succeed with message | T004 |
| FR-008: Port conflict → fail with clear message, no auto-stop | T005 |
| SC-001: Start < 2 min, both URLs reachable | T006 |
| SC-002: Task appears once, no config errors | T003, T007 |
| SC-003: Failure cause identifiable | T004, T005, T011 |
| SC-004: Audit document | T012 |
