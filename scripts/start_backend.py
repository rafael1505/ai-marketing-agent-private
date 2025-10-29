#!/usr/bin/env python3
"""
Start the backend API server with proper environment loading from .env file
This ensures .env file takes precedence over shell environment variables
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def main():
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    # Unset potentially conflicting environment variables from shell
    for key in ['OPENAI_API_KEY', 'STABILITY_API_KEY', 'REPLICATE_API_TOKEN', 'HUGGINGFACE_API_KEY']:
        if key in os.environ:
            del os.environ[key]
            print(f"🧹 Cleared shell environment variable: {key}")

    # Load environment from .env file (override=True ensures .env takes precedence)
    env_file = project_root / '.env'
    if env_file.exists():
        load_dotenv(env_file, override=True)
        print(f"✅ Loaded environment from: {env_file}")
        
        # Verify OpenAI API key
        openai_key = os.getenv('OPENAI_API_KEY', '')
        if openai_key and not openai_key.startswith('your-'):
            print(f"✅ OpenAI API Key: {openai_key[:20]}... (length: {len(openai_key)})")
        else:
            print("⚠️  Warning: OPENAI_API_KEY not properly configured")
    else:
        print(f"❌ Error: .env file not found at {env_file}")
        sys.exit(1)

    # Now start uvicorn
    print("\n🚀 Starting backend API server...")
    import uvicorn

    uvicorn.run(
        "app.main:api_app",
        host="127.0.0.1",
        port=8088,
        reload=True,
        log_level="info"
    )

if __name__ == '__main__':
    main()

