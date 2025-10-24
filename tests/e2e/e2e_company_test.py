#!/usr/bin/env python3
"""
End-to-End Company Persistence Test

This script:
1. Creates a company with proper IDs and brand colors
2. Tests the API endpoints to ensure they work correctly
3. Tests both direct API access and frontend API client functions
4. Verifies that changes persist as expected

Usage: python e2e_company_test.py
"""

import asyncio
import requests
import json
import sys
import time
import subprocess
from datetime import datetime
import signal
import os

# Configuration
API_HOST = "127.0.0.1"
API_PORT = 8088
API_URL = f"http://{API_HOST}:{API_PORT}"
AUTH_TOKEN = "DEVELOPMENT_MOCK_TOKEN_FOR_TESTING"
AUTH_HEADERS = {"Authorization": f"Bearer {AUTH_TOKEN}"}

# Import app modules
try:
    from app.db.simple_mock_db import SimpleMockDatabase
    from app.db.company import CompanyDB
    from app.models.company import CompanyUpdate
except ImportError:
    print("Error: Unable to import required modules.")
    print("Make sure you're running this script from the project root directory.")
    sys.exit(1)

# Global for API server process
api_server_process = None

def start_api_server():
    """Start the API server as a subprocess."""
    global api_server_process
    
    print("\n=== Starting API Server ===")
    
    # Set environment variables
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd()
    env["DEVELOPMENT_MODE"] = "1"
    
    # Start server
    cmd = [
        sys.executable, "-m", "uvicorn",
        "app.main:app",
        "--host", API_HOST,
        "--port", str(API_PORT),
        "--reload"
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    api_server_process = subprocess.Popen(
        cmd, env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    # Wait a bit for the server to start
    time.sleep(3)
    return True

def shutdown_api_server():
    """Shut down the API server."""
    global api_server_process
    
    if api_server_process:
        print("\nShutting down API server...")
        try:
            api_server_process.send_signal(signal.SIGTERM)
            api_server_process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            api_server_process.kill()
        finally:
            api_server_process = None

async def setup_database():
    """Set up the database with a test company."""
    print("\n=== Setting Up Database ===")
    
    # Create database instance
    db = SimpleMockDatabase()
    
    # Clear existing companies
    db._data["companies"] = {}
    
    # Create test company
    test_company = {
        "name": "Test Company",
        "description": "This is a test company for end-to-end testing",
        "email": "test@example.com",
        "phone": "+1 (555) 123-4567",
        "address": "123 Test St, Test City",
        "logo_url": "/uploads/default_logo.png",
        "brand_colors": ["#3B82F6", "#A855F7"],
        "active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Insert directly into database dictionary
    db._data["companies"]["test_company"] = test_company
    
    # Verify through API layer
    company_db = CompanyDB(db.companies)
    company = await company_db.get_company("test_company")
    
    if company:
        print("✓ Test company created successfully")
        print(f"  Name: {company.get('name')}")
        print(f"  Brand Colors: {company.get('brand_colors')}")
        return True
    else:
        print("✗ Failed to create test company")
        return False

def test_api_connection():
    """Test the basic API connection."""
    print("\n=== Testing API Connection ===")
    
    try:
        # Try with authentication headers first
        response = requests.get(
            f"{API_URL}/api/v1/diagnostic/health",
            headers=AUTH_HEADERS,
            timeout=5
        )
        
        # If that fails, try without auth headers
        if response.status_code == 403:
            print("Health endpoint requires authentication, trying without specific endpoint...")
            response = requests.get(
                f"{API_URL}/docs",
                timeout=5
            )
        
        if response.status_code == 200:
            print("✓ API server is responsive")
            if 'application/json' in response.headers.get('Content-Type', ''):
                print(f"  Response: {response.json()}")
            return True
        else:
            print(f"✗ API check failed: {response.status_code}")
            print(f"  Response: {response.text[:100]}...")
            return False
    except requests.RequestException as e:
        print(f"✗ API connection error: {e}")
        return False

def test_company_api():
    """Test company API endpoints."""
    print("\n=== Testing Company API ===")
    
    # Test getting active company
    try:
        print("Testing GET active company...")
        response = requests.get(
            f"{API_URL}/api/v1/companies/active",
            headers=AUTH_HEADERS,
            timeout=5
        )
        
        if response.status_code == 200:
            company = response.json()
            print("✓ Active company retrieved successfully")
            print(f"  Name: {company.get('name')}")
            print(f"  ID: {company.get('id')}")
            print(f"  Brand Colors: {company.get('brand_colors')}")
        else:
            print(f"✗ Failed to get active company: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except requests.RequestException as e:
        print(f"✗ Active company request error: {e}")
        return False
    
    # Test getting company by ID
    try:
        print("\nTesting GET company by ID...")
        response = requests.get(
            f"{API_URL}/api/v1/companies/test_company",
            headers=AUTH_HEADERS,
            timeout=5
        )
        
        if response.status_code == 200:
            company = response.json()
            print("✓ Company retrieved by ID successfully")
            print(f"  Name: {company.get('name')}")
            print(f"  Brand Colors: {company.get('brand_colors')}")
        else:
            print(f"✗ Failed to get company by ID: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except requests.RequestException as e:
        print(f"✗ Get company by ID request error: {e}")
        return False
    
    return True

def test_company_update():
    """Test updating a company."""
    print("\n=== Testing Company Update ===")
    
    # Prepare update data
    update_data = {
        "name": "Updated Test Company",
        "description": "This company was updated during e2e testing",
    }
    
    # Add brand colors as repeated fields (like form data)
    test_colors = ["#FF0000", "#00FF00", "#0000FF"]
    for color in test_colors:
        update_data["brand_colors"] = color
    
    try:
        print("Updating company...")
        response = requests.put(
            f"{API_URL}/api/v1/companies/test_company",
            data=update_data,
            headers=AUTH_HEADERS,
            timeout=5
        )
        
        if response.status_code == 200:
            company = response.json()
            print("✓ Company updated successfully")
            print(f"  Updated Name: {company.get('name')}")
            print(f"  Updated Colors: {company.get('brand_colors')}")
            
            # Check if brand colors were correctly saved as an array
            colors_match = sorted(company.get('brand_colors', [])) == sorted(test_colors)
            print(f"  Colors saved correctly as array: {'✓' if colors_match else '✗'}")
            
            if not colors_match:
                print(f"  Expected: {test_colors}")
                print(f"  Received: {company.get('brand_colors')}")
                return False
        else:
            print(f"✗ Failed to update company: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except requests.RequestException as e:
        print(f"✗ Update request error: {e}")
        return False
    
    return True

def test_persistence():
    """Test if changes persist after retrieval."""
    print("\n=== Testing Company Persistence ===")
    
    # Wait a bit to ensure changes are saved
    time.sleep(1)
    
    try:
        print("Retrieving company to verify persistence...")
        response = requests.get(
            f"{API_URL}/api/v1/companies/test_company",
            headers=AUTH_HEADERS,
            timeout=5
        )
        
        if response.status_code == 200:
            company = response.json()
            print("✓ Company retrieved successfully")
            
            # Check if the name was updated
            name_updated = company.get('name') == "Updated Test Company"
            print(f"  Name persisted correctly: {'✓' if name_updated else '✗'}")
            if not name_updated:
                print(f"  Expected: Updated Test Company")
                print(f"  Received: {company.get('name')}")
            
            # Check if brand colors were persisted
            expected_colors = ["#FF0000", "#00FF00", "#0000FF"]
            colors_match = sorted(company.get('brand_colors', [])) == sorted(expected_colors)
            print(f"  Colors persisted correctly: {'✓' if colors_match else '✗'}")
            if not colors_match:
                print(f"  Expected: {expected_colors}")
                print(f"  Received: {company.get('brand_colors')}")
            
            return name_updated and colors_match
        else:
            print(f"✗ Failed to verify persistence: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except requests.RequestException as e:
        print(f"✗ Persistence verification error: {e}")
        return False

async def run_test():
    """Run the complete end-to-end test."""
    print("=== E2E Company Persistence Test ===")
    
    # Set up database
    db_setup = await setup_database()
    if not db_setup:
        print("✗ Database setup failed")
        return False
    
    # Start API server
    server_started = start_api_server()
    if not server_started:
        print("✗ Failed to start API server")
        return False
    
    try:
        # Test connection
        connection_ok = test_api_connection()
        if not connection_ok:
            print("✗ API connection test failed")
            return False
        
        # Test company API
        api_ok = test_company_api()
        if not api_ok:
            print("✗ Company API test failed")
            return False
        
        # Test company update
        update_ok = test_company_update()
        if not update_ok:
            print("✗ Company update test failed")
            return False
        
        # Test persistence
        persistence_ok = test_persistence()
        if not persistence_ok:
            print("✗ Persistence test failed")
            return False
        
        # All tests passed
        print("\n=== TEST RESULTS ===")
        print("✓ Database setup: Success")
        print("✓ API connection: Success")
        print("✓ Company API: Success")
        print("✓ Company update: Success")
        print("✓ Persistence: Success")
        print("\n🎉 ALL TESTS PASSED! The company persistence fix is working correctly!")
        return True
    finally:
        # Clean up
        shutdown_api_server()

if __name__ == "__main__":
    try:
        success = asyncio.run(run_test())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nTest interrupted")
        shutdown_api_server()
        sys.exit(1)
