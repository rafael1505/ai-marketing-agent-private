# Research: Development Environment Task Audit

**Feature**: 001-dev-env-task-audit  
**Phase**: 0  
**Purpose**: Resolve technical decisions and document rationale for the single-source-of-truth task model.

---

## 1. Start task: use `docker compose up -d --wait`

**Decision**: Use `docker compose up -d --wait` for the Start task so the task does not complete until services are healthy (where supported).

**Rationale**: The architectural guideline requires "services are actually ready before the task completes." The `--wait` flag waits for containers to be in a running state; for full health checks, `docker compose` supports `--wait` with optional healthcheck configuration in the compose file. Using `--wait` avoids the task succeeding while the backend or frontend is still starting.

**Alternatives considered**:
- `docker compose up -d` only: task returns as soon as containers are created; readiness not guaranteed. Rejected per guideline.
- Custom script that polls HTTP endpoints: adds maintenance and platform-dependent logic. Rejected in favor of Compose native behavior.
- Rely on healthchecks in docker-compose.yml: if present, `--wait` can wait for them; we recommend adding simple healthchecks for web and frontend so `--wait` is meaningful. Document in implementation.

**Note**: Use Docker Compose V2 CLI (`docker compose`) only, not legacy `docker-compose`. Compose file is repo root `docker-compose.yml`. If the project's Docker Compose or Docker version does not support `--wait`, fallback to `docker compose up -d` and document that "Ready" means "containers started"; consider adding a short sleep or a one-line poll for minimal wait. Prefer upgrading Docker Compose if possible.

---

## 2. Readiness message and URLs

**Decision**: After a successful start, print:  
`Environment is READY. Backend: http://localhost:8088 | Frontend: http://localhost:3001`

**Rationale**: Spec and project constitution require backend on port 8088, frontend on 3001. Explicit "Ready" messages and URLs improve developer experience. docker-compose must expose backend on host port 8088 (constitution); if the app inside the container listens on 8000, use `"8088:8000"` in compose.

---

## 3. Single source of truth: .vscode/tasks.json only

**Decision**: One valid JSON file at `.vscode/tasks.json` containing exactly two tasks: "Start full development environment" and "Stop full development environment". All other task definitions (e.g. the duplicate second JSON block with emoji labels and mixed local/Docker tasks) are removed.

**Rationale**: Spec and guideline require centralizing all task definitions in `.vscode/tasks.json` and deterministic labels without emoji. Cursor consumes VS Code task config, so one file serves both IDEs.

**Alternatives considered**: Keeping a separate Cursor-specific task file: rejected per spec (Cursor uses .vscode/tasks.json). Keeping optional "Check status" or "Restart" tasks: allowed only if they do not duplicate or conflict with Start/Stop and are documented as optional; for minimal scope, deliver only Start + Stop first.

---

## 4. Legacy scripts: remove or deprecate

**Decision**: Identify all scripts that start/stop the full stack (or individual backend/frontend/mongo in a way that competes with Docker Compose). Remove them from the main `scripts/` path or move to `scripts/legacy/` with a README stating they are unsupported; primary path is VS Code task + Docker Compose.

**Scripts identified for removal or deprecation** (start/stop/restart of API, frontend, or mongo):

| Script | Action |
|--------|--------|
| `scripts/start_api.sh` | Remove or move to legacy (starts uvicorn locally) |
| `scripts/start_app.sh` | Remove or move to legacy (starts API + frontend + refs to mongo) |
| `scripts/start_frontend.sh` | Remove or move to legacy |
| `scripts/start_api_server.sh` | Remove or move to legacy |
| `scripts/stop_app.sh` | Remove or move to legacy |
| `scripts/start_backend.py` | Remove or move to legacy |
| `scripts/start-complete.sh` | Remove or move to legacy |
| `scripts/start-dev.sh` | Remove or move to legacy |
| `scripts/quick-start.sh` | Remove or move to legacy |
| `scripts/start-with-correct-ports.sh` | Remove or move to legacy (README currently references it) |
| `scripts/start-mongo-locally.sh` | Remove or move to legacy |
| `scripts/start-corporate.sh` | Deprecate or document as alternative for proxy environments only |
| `scripts/start_fixed_*.sh`, `scripts/restart_*.sh`, `scripts/complete-restart.sh` | Remove or move to legacy |
| `frontend/rebuild-and-start.sh` | Remove or move to legacy |

**Rationale**: Prevents configuration drift and ensures "only supported way" is Docker Compose via tasks. Scripts used only by tests (e.g. integration test runners that start uvicorn) are out of scope; only user-facing startup/stop scripts are consolidated.

---

## 5. Hot-reload in Docker Compose

**Decision**: Current docker-compose.yml does not mount backend or frontend source as volumes for live reload inside containers. For "hot-reloading so that local development remains fluid," two options: (A) Add volume mounts for backend and frontend source and use --reload / next dev inside the container; (B) Keep current build-time image and document that code changes require rebuild/restart. Prefer (A) if the team expects to edit code without rebuilding images during the day.

**Rationale**: Architectural guideline asks for "hot-reloading (volumes)." Implementing (A) may require a dev override compose file (e.g. docker-compose.override.yml) or extra service profiles so production-like builds remain unchanged. Document the chosen approach in quickstart.md.

**Recommendation**: Phase 1 implementation can keep existing compose as-is and add a short "Hot-reload" subsection in research/quickstart: "To enable live code reload, add volume mounts for backend and frontend in docker-compose.yml or use an override file." Then implement in a follow-up if needed.

---

## 6. Already running and port conflict

**Already running**: When the developer runs the start task and all services are already running, the task MUST succeed and display a short, explicit message (e.g. "Services already running" or "All services are already up"). Rely on `docker compose up -d --wait` idempotency; optionally detect "already up" and print that message so the developer is not left guessing.

**Port conflict**: When required ports (27017, 8088, 3001) are already in use, the start task MUST fail with a clear, actionable message (e.g. which port is in use and what to do—stop the process or change the port). The task MUST NOT automatically stop or kill other processes. Implement by checking port availability before `docker compose up` or by catching compose failure and mapping it to a clear message; document in quickstart.

---

## Summary Table

| Topic | Decision |
|-------|----------|
| Compose CLI | Docker Compose V2 only (`docker compose`); compose file repo root `docker-compose.yml` |
| Start command | `docker compose up -d --wait` (with fallback if --wait unavailable) |
| Readiness message | `Environment is READY. Backend: http://localhost:8088 \| Frontend: http://localhost:3001` |
| Already running | Succeed with short message (e.g. "Services already running") |
| Port conflict | Fail with clear, actionable message; no auto-stop of other processes |
| Task config | Single `.vscode/tasks.json`; two tasks only; labels without emoji |
| Legacy scripts | Remove or move to `scripts/legacy/` and document unsupported |
| Hot-reload | Document; optional volume mounts in compose for later |
