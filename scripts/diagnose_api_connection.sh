#!/bin/bash

# Diagnosis script for API connection issues
echo "===== API Connection Diagnosis ====="

# Check if the API server is running on port 8088
echo -n "Checking if port 8088 is in use: "
if lsof -i :8088 >/dev/null 2>&1; then
  echo "YES"
  lsof -i :8088
else
  echo "NO - port 8088 is not in use"
fi

echo -e "\n===== Testing API Connectivity ====="
# Try to connect to the API server with verbose output
echo "Testing root endpoint:"
curl -v http://localhost:8088/ 2>&1 | grep -E "(< HTTP|Failed to connect)"

echo -e "\nTesting companies endpoint:"
curl -v http://localhost:8088/api/v1/companies/active 2>&1 | grep -E "(< HTTP|Failed to connect)"

# Check if the Next.js frontend is using the correct API URL
echo -e "\n===== Frontend Configuration Check ====="
API_URL=$(grep -r "API_URL" /mnt/c/Users/brc07274/OneDrive\ -\ Philips/Philips\ Files/BU\ -\ CI/Repository/AI\ Marketing\ Agent\ \(Python\)/ai-marketing-agent/frontend/src/services/api.ts | head -1)
echo "Frontend API configuration: $API_URL"

# Check network interfaces
echo -e "\n===== Network Interfaces ====="
ip addr show | grep -E "inet |^[0-9]+:"

# Suggest fixes
echo -e "\n===== Recommendations ====="
echo "1. Start the API server with: cd /path/to/project && uvicorn app.main:app --host 0.0.0.0 --port 8088 --reload"
echo "2. Try accessing the API with: curl http://localhost:8088/api/v1/companies/active"
echo "3. Check if the API URL in frontend matches the actual running API server"
echo "4. If behind WSL, ensure proper network connectivity between Windows and WSL"
echo "   Run 'wsl.exe --shutdown' in Windows Powershell and restart WSL if needed"

echo -e "\n===== End of Diagnosis ====="
