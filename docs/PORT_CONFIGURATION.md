# Port Configuration Guide

## Important Port Configuration

The AI Marketing Agent application requires specific ports that must be consistent across all components to function properly.

### Required Configuration

- **API Server Port**: `8088`
- **Frontend Server Port**: `3001`
- **Frontend NextJS API Proxy**: Configured to communicate with API on port `8088`

### Common Problems

1. **ERR_CONNECTION_REFUSED errors**:
   - The most common cause is a port mismatch between the API server and frontend configuration
   - Verify API is running on port 8088, not 8089 as previously documented

2. **Cannot connect to server. Changes saved in offline mode**:
   - This error on the settings page indicates the frontend cannot reach the API
   - Use the API Connection Test tool (accessible via the diagnostic button on the settings page)

### How to Verify Correct Configuration

1. **Check API Server**:
   ```bash
   # Verify API server is running on port 8088
   curl -s "http://127.0.0.1:8088/api/v1/diagnostic/health"
   ```

2. **Check Frontend Configuration**:
   - Verify that `/frontend/next.config.js` references port 8088 in the proxy configuration
   - Verify that `/frontend/src/services/api.ts` references port 8088 in the API_URL

3. **Use the Diagnostic Tool**:
   - Access `/api-connection-test.html` in your browser
   - This tool will test connections to various API endpoints

### Starting the API Server

Always start the API server with:

```bash
cd /path/to/ai-marketing-agent
uvicorn app.main:app --host 127.0.0.1 --port 8088 --reload
```

Do not use port 8089 as it will cause connection issues with the frontend.

## Troubleshooting Tools

We've created several tools to help diagnose and fix port configuration issues:

1. **Visual Status Indicator**
   - The settings page now shows a live API connection status
   - Green indicator: Connected to correct port (8088)
   - Red indicator: Wrong port or no connection

2. **Command-line Tools**
   - `./check_api_connection.sh`: Check API connection status
   - `./fix_api_server_port.sh`: Fix issues when API is on the wrong port
   - `./start-with-correct-ports.sh`: Start everything with correct configuration

3. **Python Utilities**
   - `./port_config.py`: Standard port configuration module 
   - `./port_utils.py`: Utility to check and free required ports
   - `./fix_port_configuration.py`: Interactive tool to detect and fix port issues

4. **VS Code Tasks**
   - Run API (Mock Database): Starts API on correct port
   - Fix API Port Issues: Automatically fixes port configuration
   - Check API Connection: Tests API connectivity
   - Open API Connection Test: Opens the diagnostic web page

5. **Diagnostic Web Pages**
   - `/api-connection-test.html`: Tests API connectivity
   - `/port-configuration.html`: Visual guide to port configuration

## Common Error Messages Explained

### "Cannot connect to server. Changes saved in offline mode"
This error on the settings page indicates the frontend cannot reach the API server due to a port mismatch.

### "ERR_CONNECTION_REFUSED" in Console
This indicates the browser tried to connect to a port where no service is listening. Check that the API is running on port 8088.

## Port Configuration Utilities

### Using the New Port Utilities

We've added standardized port utilities to ensure consistent port usage:

1. **Check port availability**:
   ```bash
   python port_utils.py verify
   ```

2. **Free the API port (8088)**:
   ```bash
   python port_utils.py free-api
   ```

3. **Free the frontend port (3001)**:
   ```bash
   python port_utils.py free-frontend
   ```

4. **Free all required ports**:
   ```bash
   python port_utils.py free-all
   ```

The standard port configuration is now maintained in `port_config.py` and should be imported by all components that need port information.
