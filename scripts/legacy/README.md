# Legacy scripts (deprecated)

Scripts in this folder are **deprecated** and not supported for normal development.

**Supported way to run the full development environment**: Use the VS Code/Cursor task **"Start full development environment"** (Docker Compose). Stop with **"Stop full development environment"**. See the project README and `specs/001-dev-env-task-audit/quickstart.md`.

These legacy scripts were moved here to avoid configuration drift. They started the backend, frontend, or MongoDB in ways that compete with Docker Compose (e.g. local uvicorn, local npm, or standalone MongoDB container). Do not rely on them for new work.
