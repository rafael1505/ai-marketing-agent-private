# Quickstart: Full Development Environment (001-dev-env-task-audit)

**Audience**: Developers using Cursor or VS Code.  
**Prerequisites**: Docker and Docker Compose installed; user in Docker group (so `docker` runs without sudo).  
**Supported path**: Docker Compose via VS Code/Cursor tasks only.

---

## Start the environment

1. Open the project in **Cursor** or **VS Code**.
2. Run the task **"Start full development environment"**:
   - Command Palette → "Tasks: Run Task" → select "Start full development environment".
3. Wait until the terminal shows a readiness message, for example:
   - `Environment is READY. Backend: http://localhost:8000 | Frontend: http://localhost:3001`
4. Open in a browser:
   - **Frontend**: http://localhost:3001  
   - **Backend API (e.g. docs)**: http://localhost:8000/docs  

The task uses `docker compose up -d --wait` so services are up before the task completes. If you see permission or "command not found" errors, ensure Docker is running and your user is in the `docker` group.

---

## Stop the environment

1. Run the task **"Stop full development environment"** (Tasks: Run Task → "Stop full development environment").
2. The terminal should show a message like "Environment stopped." and all containers will be stopped.

---

## Troubleshooting

- **"permission denied" / docker socket**: Add your user to the Docker group and start a new shell, or run Docker Desktop (if on Windows/macOS) and enable integration with your environment.
- **Port already in use**: Stop any process using ports 8000, 3001, or 27017, or change the published ports in `docker-compose.yml`.
- **Task not listed**: Ensure `.vscode/tasks.json` exists and is valid JSON (single root object). Reload the editor window if needed.

No manual `uvicorn` or `npm run dev` or standalone scripts are required for the supported path; everything runs inside Docker Compose.
