# API Connection Troubleshooting Guide

This document provides step-by-step guidance for resolving the common "Cannot connect to server. Changes saved in offline mode" error on the settings page.

## Quick Fix Steps

1. **Check if the API is running on the wrong port**
   - Run: `./check_api_connection.sh`
   - If the API is detected on port 8089 (wrong port), use: `./fix_api_server_port.sh`

2. **Restart the API on the correct port**
   - Run: `uvicorn app.main:app --host 127.0.0.1 --port 8088 --reload`
   - Or use the VS Code task: "Run API (Mock Database)"

3. **Use the diagnostic tools**
   - Open: http://localhost:3000/api-connection-test.html
   - Run all tests to verify connectivity

## Root Cause: Port Configuration Mismatch

The issue occurs because:
1. The frontend is configured to connect to port 8088
2. But some documentation incorrectly stated to use port 8089
3. When the API runs on port 8089, frontend requests fail with "ERR_CONNECTION_REFUSED"

## Detailed Troubleshooting

### Step 1: Check Current API Status

```bash
# Check if API is running on port 8088 (correct)
curl -s "http://127.0.0.1:8088/api/v1/diagnostic/health"

# Check if API is mistakenly running on port 8089
curl -s "http://127.0.0.1:8089/api/v1/diagnostic/health"
```

### Step 2: Identify Running Processes

```bash
# Find processes using port 8088
lsof -i:8088

# Find processes using port 8089
lsof -i:8089
```

### Step 3: Restart with Correct Configuration

```bash
# Kill any API process on the wrong port
kill $(lsof -t -i:8089)

# Start the API on the correct port
cd /path/to/ai-marketing-agent
uvicorn app.main:app --host 127.0.0.1 --port 8088 --reload
```

### Step 4: Verify Configuration Files

These files should all reference port 8088, not 8089:

1. `/frontend/next.config.js`: Contains proxy configuration
2. `/frontend/src/services/api.ts`: Contains API URL configuration
3. `/.vscode/tasks.json`: Contains task configuration for running the API

## Error Messages Explained

### 1. "Cannot connect to server. Changes saved in offline mode"

This error occurs when:
- The frontend cannot reach the API server
- Most commonly, the API server is running on the wrong port (8089 instead of 8088)
- Or the API server is not running at all

### 2. "ERR_CONNECTION_REFUSED" in browser console

This error occurs when:
- The browser tries to make an API request to a port where no service is listening
- Check that the API is running on port 8088, not 8089

## Visual Indicators

The settings page will show:
- **Red error message**: "Cannot connect to server. Changes saved in offline mode"
- **Blue "Run API Diagnostics" button**: Click this to run the connection test tool
- **Green "Port Configuration Guide" button**: Click this to view detailed port guidance

## Additional Help

If you continue to experience issues after following these steps:

1. Check network firewall settings
2. Verify proxy configuration
3. Run the comprehensive API test suite: `./test_api_connection.py`
4. Use the automated fix script: `./fix_api_server_port.sh`

For any remaining issues, please contact the development team.
