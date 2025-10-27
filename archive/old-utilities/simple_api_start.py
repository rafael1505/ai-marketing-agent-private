#!/usr/bin/env python3
"""
Simple API Server Starter

This script starts the API server and ensures a test company is created.
It doesn't run any tests but just verifies basic functionality.
"""

import sys
import os
import subprocess
import time
from datetime import datetime
import asyncio

# Import app modules
try:
    from app.db.simple_mock_db import SimpleMockDatabase
except ImportError:
    print("Error: Unable to import required modules.")
    print("Make sure you're running this script from the project root directory.")
    sys.exit(1)

async def initialize_database():
    """Set up the database with a test company."""
    print("\n=== Initializing Database ===")
    
    # Connect to mock database
    db = SimpleMockDatabase()
    
    # Clear existing companies
    db._data["companies"] = {}
    print("Database cleared.")
    
    # Create test company
    test_company = {
        "name": "Test Company",
        "description": "This is a test company for development",
        "email": "contact@testcompany.com",
        "phone": "+1 (555) 123-4567",
        "address": "123 Test Street, Test City, TC 12345",
        "logo_url": "/uploads/default_logo.png",
        "brand_colors": ["#3B82F6", "#A855F7"],
        "active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Insert directly into the database dictionary
    db._data["companies"]["test_company"] = test_company
    print("Test company created successfully with ID: test_company")

def setup_auth_token():
    """Set up the authentication token file."""
    print("\n=== Setting up Authentication ===")
    
    # Run the authentication fix script
    subprocess.run([sys.executable, "fix_authentication.py"], check=True)

def start_api_server():
    """Start the API server."""
    print("\n=== Starting API Server ===")
    
    # Set environment variables
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd()
    env["DEVELOPMENT_MODE"] = "1"
    
    # Command to start the API server
    cmd = [
        sys.executable, "-m", "uvicorn",
        "app.main:app",
        "--host", "127.0.0.1",
        "--port", "8088",
        "--reload"
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    
    # Start the server process
    server_process = subprocess.Popen(
        cmd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    # Wait a bit for the server to start
    time.sleep(3)
    
    print("\nAPI Server started!")
    print("The API server is accessible at: http://localhost:8088")
    print("\nPress Ctrl+C to stop the server")
    
    # Monitor the server process
    try:
        while True:
            # Get output from stdout and stderr
            stdout_line = server_process.stdout.readline()
            if stdout_line:
                print(f"[API] {stdout_line.strip()}")
            
            stderr_line = server_process.stderr.readline()
            if stderr_line:
                print(f"[API ERROR] {stderr_line.strip()}")
            
            # Check if the process is still running
            if server_process.poll() is not None:
                print("API server process has terminated")
                break
            
            # Sleep to avoid high CPU usage
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nShutting down API server...")
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()
        print("API server stopped")

async def main():
    """Main entry point."""
    print("=== Simple API Server Starter ===")
    
    # 1. Initialize database
    await initialize_database()
    
    # 2. Set up authentication token
    setup_auth_token()
    
    # 3. Start API server
    start_api_server()

if __name__ == "__main__":
    asyncio.run(main())
