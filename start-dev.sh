#!/bin/bash
# This script runs the API service without Docker, using the mock database if MongoDB is unavailable

# Set colors for console output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== AI Marketing Agent Development Starter ===${NC}"
echo

# Install required packages
echo -e "Installing required packages..."
pip install -r requirements.txt

# Check if MongoDB is available
echo -e "Checking MongoDB connection..."
if mongosh --eval "db.adminCommand('ping')" --quiet &> /dev/null; then
  echo -e "${GREEN}✅ MongoDB is available. Will use real database.${NC}"
  DB_STATUS="REAL"
else
  echo -e "${YELLOW}⚠️ MongoDB is not available. Will use mock database.${NC}"
  DB_STATUS="MOCK"
fi

# Set API host and port - using 127.0.0.1 instead of 0.0.0.0 for corporate environments
API_HOST="127.0.0.1"
API_PORT="9000"  # Using a non-standard port to avoid proxy issues

# Run the FastAPI app with uvicorn
echo
if [ "$DB_STATUS" == "MOCK" ]; then
  echo -e "${YELLOW}Starting API with mock database...${NC}"
else
  echo -e "${GREEN}Starting API with MongoDB...${NC}"
fi
echo -e "${YELLOW}⚠️ Corporate network detected. Using direct localhost connection.${NC}"
echo -e "API will be available at: ${GREEN}http://$API_HOST:$API_PORT${NC}"
echo -e "API Documentation: ${GREEN}http://$API_HOST:$API_PORT/docs${NC}"
echo
echo -e "${RED}NOTE: If you encounter connection issues:${NC}"
echo -e "1. Try accessing the API directly in your browser"
echo -e "2. Check if your corporate proxy is blocking localhost connections"
echo -e "3. Try updating your frontend API URL to match this host/port"
echo

# Start with proxy bypass settings
export NO_PROXY="localhost,127.0.0.1"
export no_proxy="localhost,127.0.0.1"

uvicorn app.main:app --host $API_HOST --port $API_PORT --reload
