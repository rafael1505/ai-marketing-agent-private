# Quickstart: Full Development Environment (001-dev-env-task-audit)

**Audience**: Developers using Cursor or VS Code.  
**Prerequisites**: Docker Engine and the **Docker Compose V2 plugin** (`docker compose`, not the legacy `docker-compose`); your user in the `docker` group (`sudo usermod -aG docker $USER`, then log out/in or run `newgrp docker`); ports **8088** (backend), **3001** (frontend), and **27017** (MongoDB) must be free.  
**Supported path**: Docker Compose via VS Code/Cursor tasks only.

---

## Start the environment

**Shortcut**: Press **Ctrl+Shift+B** — this triggers the default build task ("Start full development environment") directly.

Alternatively, use the Command Palette:

```
Ctrl+Shift+P → Tasks: Run Task → Start full development environment
```

Wait until the terminal shows:

```
Environment is READY. Backend: http://localhost:8088 | Frontend: http://localhost:3001
```

All three services (MongoDB, backend, frontend) must pass their Docker healthchecks before this message appears. Open in a browser:

- **Frontend**: http://localhost:3001
- **Backend API docs**: http://localhost:8088/docs
- **Backend health**: http://localhost:8088/api/v1/diagnostic/health

The task uses `docker compose up -d --wait` (Docker Compose V2) so the readiness message is only printed after all services are healthy.

---

## Stop the environment

```
Ctrl+Shift+P → Tasks: Run Task → Stop full development environment
```

The terminal confirms shutdown with:

```
Environment stopped successfully.
```

---

## Troubleshooting

- **"permission denied" / docker socket**: Add your user to the Docker group (`sudo usermod -aG docker $USER`) and start a new shell (`newgrp docker`), or restart your session. On Windows/macOS, ensure Docker Desktop is running and WSL/system integration is enabled.
- **Port already in use**: The start task checks ports 8088, 3001, and 27017 before running. If a port is occupied, it prints which port is in use and exits with an error. Stop the process using that port — the task does **not** automatically kill other processes.
- **Services already running**: Running the start task again when everything is already up exits cleanly with `All services are already up and running at http://localhost:3001`. No restart occurs.
- **Task not listed in the Command Palette**: Ensure `.vscode/tasks.json` exists and is valid JSON (single root object with a `tasks` array). Reload the editor window (Ctrl+Shift+P → Developer: Reload Window) if needed.
- **`docker compose` not found**: Verify Docker Compose V2 is installed (`docker compose version`). If only the legacy `docker-compose` is available, install the `docker-compose-plugin` package or upgrade Docker Desktop.

No manual `uvicorn` or `npm run dev` or standalone scripts are required for the supported path; everything runs inside Docker Compose. Compose file is `docker-compose.yml` at repo root.
