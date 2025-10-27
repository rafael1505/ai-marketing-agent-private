#!/bin/bash
#!/usr/bin/env bash
# Fixed API Startup Script
# Applies company persistence fixes and starts the FastAPI server

# Configuration variables
API_PORT=8088
API_HOST="127.0.0.1"
LOG_FILE="api_server_fixed.log"

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== AI Marketing Agent API Server Startup (FIXED) ===${NC}"
echo "This script will start the API server with company persistence fixes"

# Check if the port is already in use
if netstat -tuln | grep -q ":${API_PORT} "; then
    echo -e "${RED}Error: Port ${API_PORT} is already in use.${NC}"
    echo "To use a different port, modify the API_PORT variable in this script."
    echo "To kill the existing process:"
    echo "  1. Run: lsof -i :${API_PORT}"
    echo "  2. Then: kill -9 <PID>"
    exit 1
fi

# Check if Python environment is activated
if [ -z "${VIRTUAL_ENV}" ]; then
    echo -e "${YELLOW}No Python virtual environment detected.${NC}"
    
    # Check if venv exists
    if [ -d "venv" ]; then
        echo "Activating existing virtual environment..."
        source venv/bin/activate || source venv/Scripts/activate
    else
        echo "Creating and activating new virtual environment..."
        python -m venv venv
        source venv/bin/activate || source venv/Scripts/activate
        
        # Install requirements
        echo "Installing Python dependencies..."
        pip install -r requirements.txt
    fi
else
    echo -e "${GREEN}✓ Using Python virtual environment: ${VIRTUAL_ENV}${NC}"
fi

# Create an authentication token file for development if it doesn't exist
if [ ! -f "auth_token.json" ]; then
    echo -e "${YELLOW}Creating authentication token for development...${NC}"
    echo '{"token": "DEVELOPMENT_COMPANY_PERSISTENCE_FIX_TOKEN"}' > auth_token.json
    echo -e "${GREEN}✓ Created auth_token.json${NC}"
fi

# Apply the company persistence fixes
echo -e "${YELLOW}Applying company persistence fixes...${NC}"

# Run the patch script
python patch_company_db.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Company persistence fixes applied successfully${NC}"
else
    echo -e "${RED}✗ Failed to apply company persistence fixes${NC}"
    echo "Please check the patch_company_db.py script for errors"
    exit 1
fi

# Create run script that applies patches before starting API
cat > run_fixed_api.py << EOL
#!/usr/bin/env python3

import os
import sys
import uvicorn
import importlib.util

# Apply company persistence patches
print("Applying company persistence patches...")
try:
    import patch_company_db
    patch_company_db.patch_company_db()
    test_company = patch_company_db.initialize_test_company()
    print(f"Company persistence patches applied. Test company: {test_company.get('name')}")
except Exception as e:
    print(f"Warning: Failed to apply company persistence patches: {str(e)}")

# Debug output for database state
try:
    from app.db.company import CompanyDB
    company_db = CompanyDB()
    print("Current companies in database:")
    for idx, company in enumerate(company_db.data):
        print(f"  {idx+1}. ID: {company.get('_id', 'unknown')}/{company.get('id', 'unknown')}, "
              f"Name: {company.get('name', 'unnamed')}, "
              f"Colors: {company.get('brand_colors', [])}")
except Exception as e:
    print(f"Warning: Failed to print database state: {str(e)}")

# Run the API server
if __name__ == "__main__":
    host = "${API_HOST}"
    port = ${API_PORT}
    print(f"Starting API server at http://{host}:{port}")
    uvicorn.run("app.main:app", host=host, port=port, reload=True)
EOL

# Make the run script executable
chmod +x run_fixed_api.py

# Start the API server
echo -e "${YELLOW}Starting API server with company persistence fixes...${NC}"
echo "The API will be available at http://${API_HOST}:${API_PORT}"
echo -e "API logs will be saved to ${LOG_FILE}"
echo -e "${GREEN}Press Ctrl+C to stop the server${NC}\n"

# Start the API server and log output
python run_fixed_api.py 2>&1 | tee "${LOG_FILE}"

# Exit with success
exit 0
