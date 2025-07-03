#!/usr/bin/env python3

import sys
import os
import asyncio
from fastapi.testclient import TestClient

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from app.main import api_app
    print("✓ Successfully imported api_app")
    
    # Create test client
    client = TestClient(api_app)
    
    # Test basic endpoints
    print("\n=== Testing API Endpoints ===")
    
    # Test root
    try:
        response = client.get("/")
        print(f"GET / - Status: {response.status_code}")
        if response.status_code != 404:
            print(f"Response: {response.text[:200]}")
    except Exception as e:
        print(f"GET / - Error: {e}")
    
    # Test docs
    try:
        response = client.get("/docs")
        print(f"GET /docs - Status: {response.status_code}")
    except Exception as e:
        print(f"GET /docs - Error: {e}")
    
    # Test materials endpoint
    try:
        response = client.get("/api/v1/materials/")
        print(f"GET /api/v1/materials/ - Status: {response.status_code}")
        if response.status_code < 500:
            print(f"Response: {response.text[:200]}")
    except Exception as e:
        print(f"GET /api/v1/materials/ - Error: {e}")
    
    # Test AI providers endpoint
    try:
        response = client.get("/api/v1/ai-providers/")
        print(f"GET /api/v1/ai-providers/ - Status: {response.status_code}")
        if response.status_code < 500:
            print(f"Response: {response.text[:200]}")
    except Exception as e:
        print(f"GET /api/v1/ai-providers/ - Error: {e}")
    
    print("\n✓ API testing completed")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
