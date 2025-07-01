#!/usr/bin/env python3
"""
Company Persistence Fix & API Server Startup Script

This script:
1. Initializes the database with a properly configured test_company
2. Ensures ID consistency between database and frontend
3. Starts the API server with proper error handling
4. Verifies that the API server is accessible

Usage: python startup_server.py
"""

import os
import sys
import signal
import asyncio
import subprocess
import time
import json
import requests
from datetime import datetime
import atexit

# Config
API_PORT = 8088
API_HOST = "127.0.0.1"
API_URL = f"http://{API_HOST}:{API_PORT}"
AUTH_TOKEN = "DEVELOPMENT_MOCK_TOKEN_FOR_TESTING"
AUTH_HEADERS = {"Authorization": f"Bearer {AUTH_TOKEN}"}

# Import needed modules from the application
try:
    from app.db.simple_mock_db import SimpleMockDatabase
    from app.db.company import CompanyDB
    from app.models.company import CompanyUpdate
except ImportError:
    print("Error: Unable to import required modules.")
    print("Make sure you're running this script from the project root directory.")
    sys.exit(1)

# Global for storing the API server process
api_server_process = None

def ensure_directory_exists(path):
    """Create directory if it doesn't exist."""
    if not os.path.exists(path):
        print(f"Creating directory: {path}")
        os.makedirs(path)

def cleanup():
    """Clean up resources when script exits."""
    if api_server_process:
        print("\nShutting down API server...")
        try:
            # Try graceful termination first
            api_server_process.send_signal(signal.SIGTERM)
            api_server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            print("API server didn't terminate gracefully, forcing shutdown...")
            api_server_process.kill()

# Register cleanup handler
atexit.register(cleanup)

async def initialize_database():
    """Set up the database with consistent company data."""
    print("=== Initializing Database ===")
    
    # 1. Connect to mock database
    mock_db = SimpleMockDatabase()
    company_db = CompanyDB(mock_db.companies)
    
    # 2. Clear existing companies DIRECTLY in the database dictionary
    print("\nClearing existing companies...")
    mock_db._data["companies"] = {}
    print("Database cleared.")
    
    # 3. Create a test company with consistent IDs
    print("\nCreating test company...")
    test_company = {
        "name": "Test Company",
        "description": "This is a test company for development",
        "email": "contact@testcompany.com",
        "phone": "+1 (555) 123-4567",
        "address": "123 Test Street, Test City, TC 12345",
        "logo_url": "/uploads/default_logo.png",
        "brand_colors": ["#3B82F6", "#A855F7"],
        "active": True,                # Mark as active company
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Insert the company DIRECTLY into the database dictionary
    # This ensures the correct ID is used as the dictionary key
    mock_db._data["companies"]["test_company"] = test_company
    print("Test company created successfully with ID: test_company")
    
    # 4. Verify the company exists and is properly configured
    company = await company_db.get_company("test_company")
    if company:
        print("✓ Company verification successful")
        print(f"  Name: {company.get('name')}")
        print(f"  ID: {company.get('id')}")
        print(f"  _ID: {company.get('_id')}")
        print(f"  Active: {company.get('active')}")
        print(f"  Brand Colors: {company.get('brand_colors')}")
    else:
        print("✗ Failed to verify company in database!")
        return False
    
    return True

def start_api_server():
    """Start the FastAPI server with proper environment."""
    global api_server_process
    
    print("\n=== Starting API Server ===")
    
    # Create uploads directory if it doesn't exist
    uploads_dir = os.path.join(os.getcwd(), "frontend", "public", "uploads")
    ensure_directory_exists(uploads_dir)
    
    # Set environment variables
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd()
    env["DEVELOPMENT_MODE"] = "1"
    
    try:
        # Start the API server with uvicorn
        cmd = [
            sys.executable, "-m", "uvicorn",
            "app.main:app",
            "--host", API_HOST,
            "--port", str(API_PORT),
            "--reload"
        ]
        
        print(f"Running command: {' '.join(cmd)}")
        api_server_process = subprocess.Popen(
            cmd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        # Give the server time to start
        print("Waiting for API server to start...")
        time.sleep(5)
        return True
    except Exception as e:
        print(f"Failed to start API server: {e}")
        return False

def verify_api_working():
    """Verify the API server is working correctly."""
    print("\n=== Verifying API Server ===")
    
    # Try to connect to the API health endpoint
    max_attempts = 5
    for attempt in range(1, max_attempts + 1):
        try:
            print(f"Connection attempt {attempt}/{max_attempts}...")
            response = requests.get(
                f"{API_URL}/api/v1/diagnostic/health",
                proxies={"http": None, "https": None},
                timeout=5
            )
            
            if response.status_code == 200:
                print("✓ API server is responsive")
                print(f"  Status code: {response.status_code}")
                print(f"  Response: {response.json()}")
                return True
        except requests.RequestException as e:
            print(f"  Connection failed: {e}")
        
        # Wait before trying again
        time.sleep(2)
    
    print("✗ API server verification failed after multiple attempts")
    return False

def verify_company_api():
    """Verify the company API endpoints are working."""
    print("\n=== Verifying Company API ===")
    
    try:
        # Try to get the active company
        response = requests.get(
            f"{API_URL}/api/v1/companies/active",
            headers=AUTH_HEADERS,
            proxies={"http": None, "https": None},
            timeout=5
        )
        
        if response.status_code == 200:
            company = response.json()
            print("✓ Company API is working")
            print(f"  Company name: {company.get('name')}")
            print(f"  Company ID: {company.get('id')}")
            print(f"  Brand colors: {company.get('brand_colors')}")
            return True
        else:
            print(f"✗ Company API returned error: {response.status_code}")
            print(f"  Response: {response.text}")
    except requests.RequestException as e:
        print(f"✗ Company API request failed: {e}")
    
    return False

def test_company_update():
    """Test updating the company information."""
    print("\n=== Testing Company Updates ===")
    
    # Prepare test data with typical form data format
    update_data = {
        'name': 'Updated Test Company',
        'description': 'This company was updated during startup',
    }
    
    # Add brand colors as repeated fields (like a form would)
    test_colors = ["#AA0000", "#00AA00", "#0000AA"]
    for color in test_colors:
        update_data['brand_colors'] = color
    
    try:
        # Update the company
        response = requests.put(
            f"{API_URL}/api/v1/companies/test_company",
            data=update_data,
            headers=AUTH_HEADERS,
            proxies={"http": None, "https": None},
            timeout=5
        )
        
        if response.status_code == 200:
            updated = response.json()
            print("✓ Company update successful")
            print(f"  Updated name: {updated.get('name')}")
            print(f"  Updated colors: {updated.get('brand_colors')}")
            
            # Verify colors were properly saved as an array
            colors_match = sorted(updated.get('brand_colors', [])) == sorted(test_colors)
            print(f"  Colors saved correctly as array: {'✓' if colors_match else '✗'}")
            return colors_match
        else:
            print(f"✗ Company update failed: {response.status_code}")
            print(f"  Response: {response.text}")
    except requests.RequestException as e:
        print(f"✗ Company update request failed: {e}")
    
    return False

def monitor_api_logs():
    """Monitor and display API server logs."""
    if not api_server_process:
        print("No API server process to monitor")
        return
        
    print("\n=== API Server Logs ===")
    print("Press Ctrl+C to stop the server and exit\n")
    
    try:
        while api_server_process.poll() is None:
            # Read output from stdout and stderr
            stdout_line = api_server_process.stdout.readline()
            if stdout_line:
                print(f"[API] {stdout_line.strip()}")
            
            stderr_line = api_server_process.stderr.readline()
            if stderr_line:
                print(f"[API ERROR] {stderr_line.strip()}")
                
            # Small sleep to prevent CPU hogging
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nReceived interrupt, shutting down...")
    finally:
        # Cleanup is handled by atexit

async def main():
    """Main entry point for the script."""
    print("Starting Company Persistence Fix & API Server")
    
    # 1. Initialize database with consistent company data
    db_initialized = await initialize_database()
    if not db_initialized:
        print("Failed to initialize database")
        return False
    
    # 2. Start the API server
    server_started = start_api_server()
    if not server_started:
        print("Failed to start API server")
        return False
    
    # 3. Verify API server is responsive
    api_working = verify_api_working()
    if not api_working:
        print("API server is not responding")
        return False
    
    # 4. Verify company API endpoints
    company_api_working = verify_company_api()
    if not company_api_working:
        print("Company API endpoints are not working correctly")
        return False
    
    # 5. Test company updates
    update_working = test_company_update()
    if not update_working:
        print("Company updates are not working correctly")
        
    # 6. Success message with instructions
    print("\n=== Setup Complete ===")
    print("✓ Database initialized with test_company")
    print("✓ API server running and responsive")
    print("✓ Company API endpoints verified")
    if update_working:
        print("✓ Company updates working correctly")
    else:
        print("⚠ Company updates not functioning as expected")
    
    print("\nYou can now access the application at: http://localhost:3000")
    print("The API server is accessible at: http://localhost:8088")
    print("\nMonitoring API server logs... (Ctrl+C to exit)")
    
    # 7. Monitor API server logs
    monitor_api_logs()
    
    return True

if __name__ == "__main__":
    # Run the async main function
    try:
        success = asyncio.run(main())
        if not success:
            print("\n⚠ Setup completed with errors. Check the logs above.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nSetup interrupted. Cleaning up...")
        sys.exit(0)
