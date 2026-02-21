# AI Marketing Agent

This application helps automate marketing material generation using AI tools.

## Running the full development environment (supported)

The **only supported way** to run the full development environment (MongoDB, backend, frontend) is **Docker Compose via the Cursor/VS Code task**:

1. **Start:** Run the task **"Start full development environment"** (Command Palette → Tasks: Run Task).
2. Wait until the terminal shows: `Environment is READY. Backend: http://localhost:8000 | Frontend: http://localhost:3001`
3. **Stop:** Run the task **"Stop full development environment"** when done.

**Prerequisites:**

- **Docker** and **Docker Compose** installed.
- Your user in the **Docker group** so `docker` works without sudo (e.g. `sudo usermod -aG docker $USER`, then log out and back in or use `newgrp docker`).
- Ports **8000** (backend), **3001** (frontend), and **27017** (MongoDB) available.

**Step-by-step:** See [specs/001-dev-env-task-audit/quickstart.md](specs/001-dev-env-task-audit/quickstart.md) for details and troubleshooting.

No manual `uvicorn` or `npm run dev` or standalone scripts are required for the supported path; everything runs inside Docker Compose.

---

## Database setup (Docker)

When using the supported Docker Compose setup, MongoDB runs in a container. The backend connects to it automatically. No local MongoDB install is required.

For **migrations or initial data**, run the migration script once (with the stack running or with a local MongoDB on port 27017):

```bash
python scripts/migrate_to_mongodb.py
```

This creates the `ai_marketing_agent` database, collections (users, companies, ai_providers, materials), indexes, and optional test data.

### Local MongoDB (optional)

If you run **without Docker** (e.g. backend or frontend locally), you need MongoDB installed and running.

- **Ubuntu/WSL:** `sudo apt-get install -y mongodb && sudo service mongodb start`
- **macOS:** `brew install mongodb-community && brew services start mongodb-community`
- **Windows:** Install from [mongodb.com](https://www.mongodb.com/try/download/community)

Verify: `mongo --eval "db.version()"` (or `mongosh` on newer installs).

---

## Development workflow (supported path)

1. Run the task **"Start full development environment"** (see above).
2. Open in a browser:
   - **Frontend:** http://localhost:3001
   - **API docs:** http://localhost:8000/docs
3. When done, run **"Stop full development environment"**.

---

## Running without Docker (advanced)

If you need to run the backend or frontend **outside Docker** (e.g. for debugging):

- **Backend:** Ensure MongoDB is running (local or a container). Then:  
  `uvicorn app.main:api_app --host 127.0.0.1 --port 8088 --reload`  
  (Port 8088 is for local dev; the Docker setup uses port 8000.)
- **Frontend:** `cd frontend && npm run dev`  
  (Frontend may need to point to your backend URL.)

These are **not** the primary path; the supported path is Docker Compose via the Cursor/VS Code tasks above.

---

## Legacy scripts and port notes

Scripts that previously started the stack (e.g. `start-with-correct-ports.sh`, `start-corporate.sh`, or scripts under `scripts/legacy/`) are **deprecated**. Do not rely on them for normal development. The only supported way to start/stop the full stack is the **"Start full development environment"** / **"Stop full development environment"** tasks using Docker Compose.

If you hit connection or port issues, ensure nothing else is using ports 8000, 3001, or 27017, and that you are using the URLs from the task’s readiness message (Backend: http://localhost:8000, Frontend: http://localhost:3001).

---

## Test user credentials

After running the migration script, a default test user is available:

- **Email:** demo@example.com  
- **Password:** demo123  

Verify users: `mongo ai_marketing_agent --eval "db.users.find().pretty()"` (or use MongoDB Compass).

---

## Documentation

- **Quickstart (full stack):** [specs/001-dev-env-task-audit/quickstart.md](specs/001-dev-env-task-audit/quickstart.md)
- **Development environment changelog:** [specs/001-dev-env-task-audit/CHANGELOG.md](specs/001-dev-env-task-audit/CHANGELOG.md)
- **MongoDB architecture:** [docs/MONGODB_ARCHITECTURE.md](docs/MONGODB_ARCHITECTURE.md)
- **Migration summary:** [docs/MIGRATION_SUMMARY.md](docs/MIGRATION_SUMMARY.md)
