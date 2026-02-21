#!/bin/bash
# API startup script with proxy bypass for local development

# Set no_proxy for local development
export no_proxy="localhost,127.0.0.1,*.local"
export NO_PROXY="localhost,127.0.0.1,*.local"

echo "Starting AI Marketing Agent API on port 8088..."
echo "Proxy bypass configured for local development"

# Check if port is in use
if lsof -Pi :8088 -sTCP:LISTEN -t >/dev/null ; then
    echo "Port 8088 is in use. Killing existing processes..."
    pkill -f "uvicorn app.main:api_app"
    sleep 2
fi

# Start the API server
uvicorn app.main:api_app --host 127.0.0.1 --port 8088 --reload
