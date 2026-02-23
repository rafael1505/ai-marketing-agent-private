# Changelog: Development Environment Task Audit (001-dev-env-task-audit)

**Date completed**: 2026-02-19  
**Branch**: `001-dev-env-task-audit`  
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

---

## Summary

This feature unified all development environment startup and shutdown logic under two canonical VS Code / Cursor tasks backed by Docker Compose V2. All legacy startup scripts were deprecated, the backend port was aligned to the project constitution, and the task scripts were enhanced with explicit user-facing feedback for three scenarios: cold start, already-running, and port conflict.

---

## Changes

### 1. Backend port aligned to project constitution (`docker-compose.yml`)

**Before**: `web` service exposed host port **8000** (`"8000:8000"`).  
**After**: `web` service exposes host port **8088** (`"8088:8000"`). The container-internal port (8000) is unchanged; only the host mapping changed.

Files changed:
- `docker-compose.yml` — port mapping and `NEXT_PUBLIC_API_URL` environment variable
- `README.md` — all URL references updated
- `specs/001-dev-env-task-audit/CHANGELOG.md`, `research.md`, `quickstart.md`, `contracts/task-definition.md` — URL references updated

---

### 2. `.vscode/tasks.json` replaced with a single canonical configuration

**Before**: File contained a mix of tasks including emoji-labelled entries (🚀, 🛑), `sg docker`-wrapped commands, legacy local-dev tasks ("Start MongoDB only", "Check Services Status"), and duplicate JSON blocks.

**After**: Single valid JSON object with exactly two tasks:

| Label | Command | Notes |
|---|---|---|
| `Start full development environment` | `bash scripts/start-dev-env.sh` | Default build task (`Ctrl+Shift+B`); calls helper script |
| `Stop full development environment` | `echo 'Stopping...' && docker compose down && echo 'Environment stopped successfully.'` | Inline; simple and deterministic |

- No `sg docker` wrapper — runs `docker compose` directly.
- Start task set as default build task (`"group": {"kind": "build", "isDefault": true}`).
- Docker Compose V2 CLI (`docker compose`) used throughout; legacy `docker-compose` removed.

---

### 3. Start task helper script (`scripts/start-dev-env.sh`)

A dedicated helper script was introduced to keep `.vscode/tasks.json` readable while implementing the three-scenario logic required by the spec.

**Execution order**:

1. **Already-running check** (T004): `docker compose ps -q` detects any running containers.  
   - If running → print `All services are already up and running at http://localhost:3001` and exit 0.  
   - Must run before the port check so Docker's own ports are not misidentified as conflicts.

2. **Port-conflict check** (T005): `lsof` probes ports 27017, 8088, and 3001.  
   - If any port is occupied by an external process → print a per-port `ERROR` line, then print the consolidated actionable message, and exit 1.  
   - Task does **not** kill or stop any processes automatically.  
   - Gracefully skipped if `lsof` is not installed.

3. **Compose start**: `docker compose up -d --wait`  
   - `--wait` blocks until every service passes its Docker healthcheck before printing the readiness message.  
   - On success → `Environment is READY. Backend: http://localhost:8088 | Frontend: http://localhost:3001`

---

### 4. Docker Compose healthchecks verified (`docker-compose.yml`)

All three services had healthchecks confirmed present and correct:

| Service | Healthcheck target | Notes |
|---|---|---|
| `mongo` | `mongo --eval "db.adminCommand('ping')"` | Inside container |
| `web` | `http://localhost:8000/api/v1/diagnostic/health` | Inside container (host port is 8088) |
| `frontend` | `http://127.0.0.1:3001` | Inside container |

`docker compose config` exits 0 with no warnings.

---

### 5. Legacy startup/stop scripts moved to `scripts/legacy/`

All scripts that previously offered an alternative way to start or stop the stack were moved to `scripts/legacy/` and marked unsupported via `scripts/legacy/README.md`.

Scripts moved (25 total), including:

- `start_api.sh`, `start_app.sh`, `start_frontend.sh`, `start_api_server.sh`
- `start-complete.sh`, `start-dev.sh`, `quick-start.sh`
- `start-with-correct-ports.sh`, `start-mongo-locally.sh`, `start-corporate.sh`
- `start_backend.py`, `stop_app.sh`
- `start_fixed_api.sh`, `start_fixed_frontend.sh`
- `restart_api.sh`, `restart_api_clean.sh`, `restart_api_server.sh`, `restart-frontend.sh`
- `complete-restart.sh`, `debug_restart_api.sh`, `start-backend-with-env.sh`
- `rebuild-and-start.sh` (frontend), `rebuild-frontend.sh`
- `ensure_api_port.sh` (auto-killed processes on port 8088; violates no-auto-kill rule)

Scripts intentionally kept in `scripts/` root:

| Script | Reason |
|---|---|
| `start.sh` | Docker container entrypoint; referenced by `docker-compose.yml` |
| `start-dev-env.sh` | New T004/T005 helper, called by the VS Code task |
| `start_test_api.sh` | Test helper (port 8089); out of scope per research.md |

---

### 6. README rewritten

`README.md` was rewritten to reflect the new single supported path:

- Added prerequisite table: Docker Engine, Docker Compose V2 plugin, Docker group membership, free ports.
- Documents `Ctrl+Shift+B` as the shortcut for the Start task.
- Removed all primary references to `uvicorn`, `npm run dev`, and legacy scripts; these are qualified as advanced/unsupported only.
- Added service URL table (frontend, backend health, Swagger docs).
- Links to `specs/001-dev-env-task-audit/quickstart.md` for detailed walkthrough and troubleshooting.

---

## Spec requirements coverage

| Requirement | Status | Implemented by |
|---|---|---|
| FR-001: Docker Compose V2 only; health-check completion | ✅ | T002, T003, T006 |
| FR-002: No sudo required when user is in docker group | ✅ | T003 (no `sg docker`) |
| FR-002b: Explicit user-facing messages (Starting, READY, Stopping, stopped) | ✅ | T003, T009 |
| FR-003: Single valid `.vscode/tasks.json`; no duplicates | ✅ | T003, T007 |
| FR-003b: Canonical labels, no emoji | ✅ | T003, T007 |
| FR-004: Identifiable failure messages | ✅ | T003, T005 |
| FR-005: Audit document | ✅ | T012 (this file) |
| FR-006: Stop task required | ✅ | T003, T009 |
| FR-007: Already running → succeed with short message | ✅ | T004 |
| FR-008: Port conflict → fail with clear message; no auto-stop | ✅ | T005 |
| SC-001: Start < 2 min, both URLs reachable after task | ✅ | T006 (verified: ~20s cold start) |
| SC-002: Task appears once in list, no config errors | ✅ | T003, T007 |
| SC-003: Failure cause identifiable from terminal output | ✅ | T004, T005 |
| SC-004: Audit document present | ✅ | T012 (this file) |

---

## How to run the full stack (current)

1. Open the project in Cursor or VS Code.
2. Press **Ctrl+Shift+B**, or: Command Palette → **Tasks: Run Task** → **Start full development environment**.
3. Wait for: `Environment is READY. Backend: http://localhost:8088 | Frontend: http://localhost:3001`
4. When done: Command Palette → **Tasks: Run Task** → **Stop full development environment**.

See [quickstart.md](./quickstart.md) for step-by-step instructions and troubleshooting.
