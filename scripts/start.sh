#!/bin/bash
# Start the application
exec uvicorn app.main:api_app --host 0.0.0.0 --port 8000
