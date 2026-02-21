# Changelog: Development environment task audit (001-dev-env-task-audit)

Summary of changes from the previous VS Code–oriented setup to the current single supported path.

## What changed

- **Single valid `.vscode/tasks.json`**  
  The file is one JSON object with exactly two tasks:
  - **Start full development environment** – runs `docker compose up -d --wait` and prints a readiness message with backend and frontend URLs.
  - **Stop full development environment** – runs `docker compose down` and confirms shutdown.

- **Docker Compose only for the full stack**  
  The only supported way to run the full development environment (MongoDB, backend, frontend) is via the above Cursor/VS Code tasks, which use Docker Compose. No mixed mode (local uvicorn + local npm + Docker Mongo) for the canonical start/stop flow.

- **Legacy startup/stop scripts moved**  
  Scripts that duplicated full-stack start/stop (e.g. `start_api.sh`, `start_app.sh`, `start-complete.sh`, `quick-start.sh`, `start-corporate.sh`, various `restart_*` and `start_fixed_*` scripts, and `frontend/rebuild-and-start.sh`) were moved to `scripts/legacy/`. They are deprecated; see `scripts/legacy/README.md`.

- **README updated**  
  The main README now states that Docker Compose via the VS Code/Cursor tasks is the only supported path, documents prerequisites (Docker, Docker Compose, user in Docker group; ports 8000, 3001, 27017), and points to [quickstart.md](./quickstart.md) for steps. Instructions that said “run uvicorn…”, “run npm run dev”, or “use script X” as the primary way to start the stack were removed or qualified as advanced/legacy.

- **Healthchecks and task reliability**  
  `docker-compose.yml` was given healthchecks for `mongo`, `web`, and `frontend` so `docker compose up -d --wait` waits until services are ready. Tasks run the compose commands via `sg docker` where needed so they work in Cursor even when the terminal session does not have the Docker group.

## How to run the full stack (current)

1. Open the project in Cursor or VS Code.
2. Run the task **“Start full development environment”**.
3. Use Backend: http://localhost:8000 and Frontend: http://localhost:3001 (as shown in the task output).
4. When done, run **“Stop full development environment”**.

See [quickstart.md](./quickstart.md) for details and troubleshooting.
