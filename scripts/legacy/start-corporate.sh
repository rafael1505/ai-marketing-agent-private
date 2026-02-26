#!/bin/bash
# This script starts the application in a corporate environment with proxy restrictions

# Set colors for console output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== AI Marketing Agent - Corporate Environment Setup ===${NC}"
echo

echo -e "${YELLOW}This script will start the application in a way that works around proxy restrictions${NC}"
echo

# Kill any existing processes
echo "Stopping any existing processes..."
pkill -f uvicorn || echo "No API processes to stop"
pkill -f "npm run dev" || echo "No frontend processes to stop"

# Setup proxy bypass
export NO_PROXY="localhost,127.0.0.1"
export no_proxy="localhost,127.0.0.1"
export NODE_TLS_REJECT_UNAUTHORIZED=0

# Start the API with mock database
echo -e "${GREEN}Starting API with mock database...${NC}"
cd "$(dirname "$0")"
nohup python -m uvicorn app.main:app --host 127.0.0.1 --port 9000 --reload > api_logs.txt 2>&1 &
API_PID=$!
echo "API started with PID: $API_PID"
echo "API will be available at: http://127.0.0.1:9000"

# Update the frontend environment file (Next.js reads frontend/.env.local, not frontend/.env/.env.local).
# This script starts the API on port 9000, so frontend must point to 9000. For Docker backend (8088), use frontend/.env.local with NEXT_PUBLIC_API_URL=http://localhost:8088/api/v1.
echo -e "${GREEN}Configuring frontend...${NC}"
echo "NEXT_PUBLIC_API_URL=http://127.0.0.1:9000/api/v1" > frontend/.env.local
echo "NODE_TLS_REJECT_UNAUTHORIZED=0" >> frontend/.env.local

# Wait for API to start
echo "Waiting for API to initialize..."
sleep 5

# Start the frontend
echo -e "${GREEN}Starting frontend...${NC}"
cd frontend
nohup npm run dev -- --port 3900 --hostname 127.0.0.1 > ../frontend_logs.txt 2>&1 &
FRONTEND_PID=$!
echo "Frontend started with PID: $FRONTEND_PID"
echo "Frontend will be available at: http://127.0.0.1:3900"

echo
echo -e "${GREEN}=== Application Started ===${NC}"
echo -e "API:      ${BLUE}http://127.0.0.1:9000${NC}"
echo -e "API Docs: ${BLUE}http://127.0.0.1:9000/docs${NC}"
echo -e "Frontend: ${BLUE}http://127.0.0.1:3900${NC}"
echo
echo -e "${YELLOW}NOTE: You need to access these URLs directly in your browser.${NC}"
echo -e "${YELLOW}If you still have connection issues, please verify your corporate proxy settings.${NC}"
echo
echo -e "Log files:"
echo -e " - API logs: ${BLUE}$(pwd)/../api_logs.txt${NC}"
echo -e " - Frontend logs: ${BLUE}$(pwd)/../frontend_logs.txt${NC}"
echo
echo -e "To stop the application, run: ${RED}pkill -f uvicorn; pkill -f \"npm run dev\"${NC}"
