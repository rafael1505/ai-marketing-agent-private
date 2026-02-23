#!/bin/bash

echo "Testing API connection..."
curl -v http://localhost:8088/api/v1/companies/active

echo -e "\n\nTesting if API server is running..."
if lsof -i :8088; then
    echo "API server is running on port 8088"
else
    echo "No process is using port 8088"
fi
