#!/bin/bash
# Script to clear Next.js cache and restart the frontend

echo "Stopping any existing Next.js processes..."
pkill -f "next dev" || true

echo "Killing any processes using port 3001 (Linux)..."
if command -v lsof &> /dev/null; then
  for pid in $(lsof -t -i:3001 2>/dev/null); do
    echo "Killing process $pid"
    kill -9 $pid 2>/dev/null || true
  done
else
  echo "lsof not found, trying alternative method"
  fuser -k 3001/tcp 2>/dev/null || true
fi

echo "Killing any processes using port 3001 (Windows)..."
# Try to kill the process on Windows side if it's using the port
powershell.exe -Command "foreach ($process in Get-NetTCPConnection -LocalPort 3001 -ErrorAction SilentlyContinue) { Stop-Process -Id $process.OwningProcess -Force -ErrorAction SilentlyContinue }" || true

echo "Removing Next.js build cache..."
cd "/mnt/c/Users/brc07274/OneDrive - Philips/Philips Files/BU - CI/Repository/AI Marketing Agent (Python)/ai-marketing-agent/frontend"
rm -rf .next

echo "Clearing npm cache..."
npm cache clean --force

echo "Waiting 2 seconds for ports to be released..."
sleep 2

echo "Starting frontend in development mode..."
echo "Access the application at: http://localhost:3001"
cd "/mnt/c/Users/brc07274/OneDrive - Philips/Philips Files/BU - CI/Repository/AI Marketing Agent (Python)/ai-marketing-agent/frontend" 
npm run dev -- --port 3001 --host 127.0.0.1
