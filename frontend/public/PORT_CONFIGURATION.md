# API Port Configuration Guide

## Important Port Configuration

The AI Marketing Agent application uses a specific port configuration that must be consistent across all components to function properly.

### Required Configuration

- **API Server Port**: `8088`
- **Frontend NextJS API Proxy**: Configured to communicate with port `8088`

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
