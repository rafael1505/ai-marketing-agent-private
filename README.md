# AI Marketing Agent

This application automates marketing material generation using AI providers configured via a database-driven registry.

---

## Quick start

The **only supported way** to run the full development environment (MongoDB, backend, frontend) is via the **Docker Compose task** built into Cursor and VS Code.

### 1. Prerequisites

| Requirement | Notes |
|---|---|
| **Docker Engine** | [Install Docker](https://docs.docker.com/engine/install/) |
| **Docker Compose V2** | Comes bundled with Docker Desktop; on Linux, install the `docker-compose-plugin` package. Use `docker compose` (not the legacy `docker-compose`). |
| **Docker group membership** | Linux / WSL: `sudo usermod -aG docker $USER`, then log out and back in (or run `newgrp docker` in the current session). |
| **Free ports** | **8088** (backend), **3001** (frontend), **27017** (MongoDB). Nothing else may bind these ports when starting. |

### 2. Start the environment

Open the project in Cursor or VS Code, then press **Ctrl+Shift+B** (default build task), or use the Command Palette:

```
Command Palette (Ctrl+Shift+P) → Tasks: Run Task → Start full development environment
```

Wait for the terminal to print:

```
Environment is READY. Backend: http://localhost:8088 | Frontend: http://localhost:3001
```

All three services (MongoDB, backend, frontend) must pass their Docker healthchecks before this message appears.

### 3. Verify

| Service | URL |
|---|---|
| Frontend | http://localhost:3001 |
| Backend API | http://localhost:8088/api/v1/diagnostic/health |
| API docs (Swagger) | http://localhost:8088/docs |

### 4. Stop the environment

```
Command Palette → Tasks: Run Task → Stop full development environment
```

The terminal will confirm with `Environment stopped successfully.`

**Detailed walkthrough and troubleshooting:** [specs/001-dev-env-task-audit/quickstart.md](specs/001-dev-env-task-audit/quickstart.md)

---

## Database setup

MongoDB runs as a Docker container and requires no local installation.

To seed the database or run migrations, execute the migration script once while the stack is running:

```bash
python scripts/migrate_to_mongodb.py
```

This creates the `ai_marketing_agent` database, collections (`users`, `companies`, `ai_providers`, `materials`), indexes, and optional test data.

### Test credentials (after migration)

| Field | Value |
|---|---|
| Email | demo@example.com |
| Password | demo123 |

To verify: `mongosh ai_marketing_agent --eval "db.users.find().pretty()"` (or use [MongoDB Compass](https://www.mongodb.com/products/compass)).

---

## Running without Docker (advanced)

> **Not the supported path.** Use the Docker Compose task above for day-to-day development.

If you need to run individual services outside Docker for debugging:

- **Backend:** Ensure MongoDB is reachable (local or containerised), then:
  ```bash
  uvicorn app.main:api_app --host 127.0.0.1 --port 8088 --reload
  ```
- **Frontend:** `cd frontend && npm run dev`

Note that `next.config.js` already proxies `/api/*` and `/diagnostic/*` to `http://127.0.0.1:8088`, so the frontend works against a locally-running backend without further configuration.

---

## Legacy scripts

Scripts previously used to start the stack (e.g. `start-with-correct-ports.sh`, `start-corporate.sh`) have been moved to `scripts/legacy/` and are unsupported. See `scripts/legacy/README.md`.

---

## Documentation

| Document | Description |
|---|---|
| [specs/001-dev-env-task-audit/quickstart.md](specs/001-dev-env-task-audit/quickstart.md) | Step-by-step quickstart and troubleshooting |
| [specs/001-dev-env-task-audit/CHANGELOG.md](specs/001-dev-env-task-audit/CHANGELOG.md) | Development environment change history |
| [docs/MONGODB_ARCHITECTURE.md](docs/MONGODB_ARCHITECTURE.md) | MongoDB collection and data model reference |
| [docs/SDD_MIGRATION_SUMMARY.md](docs/SDD_MIGRATION_SUMMARY.md) | Spec-Driven Development (Spec Kit) migration summary |
