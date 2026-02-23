#!/usr/bin/env bash
# Start script for the full development environment.
# Called by the VS Code / Cursor task "Start full development environment".
# Must be run from the repo root (tasks.json sets cwd to ${workspaceFolder}).

echo 'Starting...'

# T004: Check if services are already running.
# This check must come before the port-conflict check so that ports held by
# Docker's own containers are not misidentified as external conflicts.
RUNNING=$(docker compose ps -q 2>/dev/null || true)
if [ -n "$RUNNING" ]; then
  echo 'All services are already up and running at http://localhost:3001'
  exit 0
fi

# T005: Check for port conflicts before attempting to start.
# lsof is standard on Linux/macOS/WSL2. If unavailable, this block is skipped
# and Docker Compose will surface its own bind error.
CONFLICT=0
if command -v lsof >/dev/null 2>&1; then
  for PORT in 27017 8088 3001; do
    if lsof -i:"$PORT" -sTCP:LISTEN -t >/dev/null 2>&1; then
      echo "ERROR: Port $PORT is already in use by another process."
      CONFLICT=1
    fi
  done
fi

if [ "$CONFLICT" -eq 1 ]; then
  echo "Port conflict detected. Please ensure ports 8088, 3001, and 27017 are free or run the 'Stop' task first."
  exit 1
fi

# Start all services and wait until every healthcheck passes.
docker compose up -d --wait \
  && echo 'Environment is READY. Backend: http://localhost:8088 | Frontend: http://localhost:3001'
