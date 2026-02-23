# Data Model: Task Configuration (Development Environment Audit)

**Feature**: 001-dev-env-task-audit  
**Phase**: 1  
**Scope**: Structure of `.vscode/tasks.json` and the two canonical tasks. No domain database entities are introduced.

---

## Entity: Task Configuration File

**File**: `.vscode/tasks.json`  
**Format**: Single JSON object conforming to VS Code Tasks 2.0 schema.

**Attributes**:
- `version`: `"2.0.0"`
- `tasks`: array of task objects (exactly two for this feature: Start, Stop)

**Validation rules**:
- File MUST be valid JSON (one root object; no concatenated JSON blocks).
- `tasks` MUST contain exactly one task with `label` "Start full development environment" and exactly one with `label` "Stop full development environment".
- No task label MUST contain emoji or other non-ASCII decorative characters in the canonical labels.

---

## Entity: Start full development environment (task)

**Label**: `"Start full development environment"` (exact string).  
**Type**: `shell`.

**Required attributes**:
- `label`: "Start full development environment"
- `type`: "shell"
- `command`: Shell command that (1) starts all services via Docker Compose, (2) waits for readiness where possible, (3) prints explicit "Starting..." and "Environment is READY" (or equivalent) messages.
- `options.cwd`: `"${workspaceFolder}"`

**Recommended command shape** (from research.md): Use Docker Compose V2 (`docker compose`); working directory repo root; compose file `docker-compose.yml` at repo root. Task completes only after health check (use `docker compose up -d --wait`). When already running, succeed with message "Services already running" or equivalent.
```text
echo "Starting..." && docker compose up -d --wait && echo "Environment is READY. Backend: http://localhost:8088 | Frontend: http://localhost:3001"
```

**Optional**: `detail`, `problemMatcher`, `presentation` per VS Code schema.

**State**: N/A (task is stateless; success = exit code 0).

---

## Entity: Stop full development environment (task)

**Label**: `"Stop full development environment"` (exact string).  
**Type**: `shell`.

**Required attributes**:
- `label`: "Stop full development environment"
- `type`: "shell"
- `command`: Shell command that stops all services (e.g. `docker compose down`) and prints clear feedback (e.g. "Stopping...", "Environment stopped.").
- `options.cwd`: `"${workspaceFolder}"`

**Recommended command shape**:
```text
echo "Stopping..." && docker compose down && echo "Environment stopped."
```

**Optional**: `detail`, `problemMatcher`, `presentation`.

---

## Relationships

- The **task configuration file** contains exactly two **tasks** (Start and Stop).
- There is no reference from tasks to external scripts; commands are self-contained shell one-liners (or minimal inline sequences) so that the single source of truth remains the file itself.

---

## Out of scope (no data model)

- Docker Compose service definitions (already exist in `docker-compose.yml`).
- Backend/frontend domain entities (unchanged by this feature).
- Legacy script parameters or return codes (those scripts are deprecated/removed).
