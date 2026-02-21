#!/bin/bash

# AI Marketing Agent - Backend Startup Script with Environment Loading
# This script ensures that .env file takes precedence over shell environment variables

cd "$(dirname "$0")/.."

echo "🔧 Loading environment variables from .env file..."

# Unset potentially conflicting environment variables
unset OPENAI_API_KEY
unset STABILITY_API_KEY
unset REPLICATE_API_TOKEN
unset HUGGINGFACE_API_KEY

# Load environment from .env file (exclude comments and empty lines, handle special characters)
if [ -f .env ]; then
    set -a  # automatically export all variables
    source <(grep -v '^#' .env | grep -v '^$' | grep '=')
    set +a
    echo "✅ Environment variables loaded from .env"
    
    # Verify OpenAI API key is loaded
    if [ -n "$OPENAI_API_KEY" ]; then
        KEY_START=$(echo "$OPENAI_API_KEY" | cut -c1-20)
        KEY_LENGTH=${#OPENAI_API_KEY}
        echo "✅ OpenAI API Key: ${KEY_START}... (length: ${KEY_LENGTH})"
    else
        echo "⚠️  Warning: OPENAI_API_KEY not found in .env"
    fi
else
    echo "❌ Error: .env file not found"
    exit 1
fi

echo ""
echo "🚀 Starting backend API server..."
uvicorn app.main:api_app --host 127.0.0.1 --port 8088 --reload
