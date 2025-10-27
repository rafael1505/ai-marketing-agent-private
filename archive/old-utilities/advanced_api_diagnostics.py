#!/usr/bin/env python3
"""
Advanced API Diagnostic Tool
This script performs comprehensive API connectivity and authentication tests
for the AI Marketing Agent application.
"""

import requests
import json
import os
import sys
import time
from datetime import datetime
import urllib3

# Disable insecure request warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ANSI color codes for terminal output
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[0;33m'
BLUE = '\033[0;34m'
CYAN = '\033[0;36m'
NC = '\033[0m'  # No Color

# Configuration
API_URL_8088 = "http://127.0.0.1:8088/api/v1"
API_URL_8089 = "http://127.0.0.1:8089/api/v1"
TEST_USERNAME = "test@example.com"
TEST_PASSWORD = "password"
FRONTEND_URL = "http://localhost:3001"

def print_header(message):
    """Print a formatted header."""
    print(f"\n{BLUE}{'=' * 40}{NC}")
    print(f"{BLUE}{message}{NC}")
    print(f"{BLUE}{'=' * 40}{NC}")

def print_status(message, status, details=None):
    """Print a status message with color based on success/failure."""
    if status == "success":
        prefix = f"{GREEN}✅ SUCCESS:{NC}"
    elif status == "warning":
        prefix = f"{YELLOW}⚠️ WARNING:{NC}"
    elif status == "error":
        prefix = f"{RED}❌ ERROR:{NC}"
    else:
        prefix = f"{CYAN}ℹ️ INFO:{NC}"
    
    print(f"{prefix} {message}")
    
    if details:
        if isinstance(details, dict) or isinstance(details, list):
            # Pretty print JSON data
            print(json.dumps(details, indent=2))
        else:
            print(f"  {details}")

def test_api_connection(url, endpoint="/diagnostic/ping"):
    """Test connection to API endpoint."""
    full_url = f"{url}{endpoint}"
    print(f"Testing connection to: {full_url}")
    
    try:
        # Use noproxy to bypass any proxy settings
        response = requests.get(
            full_url, 
            timeout=5, 
            verify=False,
            headers={"Cache-Control": "no-cache", "Pragma": "no-cache"}
        )
        
        if response.status_code == 200:
            print_status(f"Connected to {url}", "success", response.json())
            return True, response.json()
        else:
            print_status(
                f"Connection failed with status code: {response.status_code}", 
                "error",
                response.text
            )
            return False, None
    except requests.exceptions.ConnectionError:
        print_status(f"Connection refused to {url}", "error", "Server might not be running")
        return False, None
    except requests.exceptions.ReadTimeout:
        print_status(f"Connection timed out to {url}", "error", "Server might be hanging")
        return False, None
    except Exception as e:
        print_status(f"Connection error to {url}", "error", str(e))
        return False, None

def test_authentication():
    """Test authentication with test credentials."""
    print_header("Testing Authentication")
    
    try:
        # First check if API is accessible
        connected, _ = test_api_connection(API_URL_8088)
        if not connected:
            print_status("Skipping authentication test as API is not accessible", "warning")
            return False, None
        
        auth_url = f"{API_URL_8088}/auth/login"
        print(f"Testing authentication at: {auth_url}")
        
        # Use form data for authentication
        response = requests.post(
            auth_url,
            data={"username": TEST_USERNAME, "password": TEST_PASSWORD},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=5,
            verify=False
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            if token:
                # Create a redacted view for display
                token_display = {
                    "token_type": data.get("token_type"),
                    "access_token": f"{token[:10]}...{token[-10:]}" if token else "None",
                    "token_length": len(token) if token else 0
                }
                print_status("Authentication successful", "success", token_display)
                
                # Save token to file for further testing
                with open("auth_token_fresh.json", "w") as f:
                    json.dump(data, f, indent=2)
                print_status("Token saved to auth_token_fresh.json", "info")
                
                return True, token
            else:
                print_status("Authentication response doesn't contain token", "error", data)
                return False, None
        else:
            print_status(
                f"Authentication failed with status code: {response.status_code}", 
                "error", 
                response.text
            )
            return False, None
    except Exception as e:
        print_status("Authentication error", "error", str(e))
        return False, None

def test_protected_endpoint(token=None):
    """Test access to a protected endpoint with token."""
    print_header("Testing Protected Endpoint")
    
    if not token:
        # Try to load token from file
        try:
            with open("auth_token_fresh.json", "r") as f:
                data = json.load(f)
                token = data.get("access_token")
        except Exception as e:
            print_status("Failed to load token from file", "error", str(e))
            return False
    
    if not token:
        print_status("No token available for testing protected endpoint", "error")
        return False
    
    try:
        protected_url = f"{API_URL_8088}/diagnostic/protected"
        print(f"Testing protected endpoint: {protected_url}")
        
        response = requests.get(
            protected_url,
            headers={"Authorization": f"Bearer {token}"},
            timeout=5,
            verify=False
        )
        
        if response.status_code == 200:
            print_status("Successfully accessed protected endpoint", "success", response.json())
            return True
        else:
            print_status(
                f"Failed to access protected endpoint: {response.status_code}", 
                "error", 
                response.text
            )
            return False
    except Exception as e:
        print_status("Error accessing protected endpoint", "error", str(e))
        return False

def test_company_endpoint(token=None):
    """Test the companies endpoint which was having issues."""
    print_header("Testing Companies Endpoint")
    
    if not token:
        # Try to load token from file
        try:
            with open("auth_token_fresh.json", "r") as f:
                data = json.load(f)
                token = data.get("access_token")
        except Exception as e:
            print_status("Failed to load token from file", "error", str(e))
            return False
    
    if not token:
        print_status("No token available for testing companies endpoint", "error")
        return False
    
    try:
        companies_url = f"{API_URL_8088}/companies/active"
        print(f"Testing companies endpoint: {companies_url}")
        
        response = requests.get(
            companies_url,
            headers={"Authorization": f"Bearer {token}"},
            timeout=5,
            verify=False
        )
        
        if response.status_code == 200:
            print_status("Successfully accessed companies endpoint", "success", response.json())
            return True
        else:
            print_status(
                f"Failed to access companies endpoint: {response.status_code}", 
                "error", 
                response.text
            )
            return False
    except Exception as e:
        print_status("Error accessing companies endpoint", "error", str(e))
        return False

def test_proxy_bypass():
    """Test if corporate proxy is causing issues."""
    print_header("Testing Proxy Bypass")
    
    # Try with different proxy settings
    proxies = {
        "http": None,
        "https": None
    }
    
    try:
        response = requests.get(
            f"{API_URL_8088}/diagnostic/ping",
            proxies=proxies,
            timeout=5,
            verify=False
        )
        
        if response.status_code == 200:
            print_status("Successfully connected with proxy bypass", "success", response.json())
            return True
        else:
            print_status(
                f"Failed to connect with proxy bypass: {response.status_code}", 
                "error", 
                response.text
            )
            return False
    except Exception as e:
        print_status("Error with proxy bypass", "error", str(e))
        return False

def check_frontend_server():
    """Check if frontend server is running."""
    print_header("Checking Frontend Server")
    
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print_status("Frontend server is running", "success")
            return True
        else:
            print_status(
                f"Frontend server returned status code: {response.status_code}", 
                "warning", 
                response.text[:100] + "..."
            )
            return False
    except Exception as e:
        print_status("Frontend server appears to be down", "error", str(e))
        return False

def generate_report(results):
    """Generate a comprehensive report."""
    print_header("Diagnostic Report Summary")
    
    # Count successes and failures
    success_count = sum(1 for r in results if r["status"] == "success")
    warning_count = sum(1 for r in results if r["status"] == "warning")
    error_count = sum(1 for r in results if r["status"] == "error")
    
    print(f"{GREEN}{success_count} Successful tests{NC}")
    print(f"{YELLOW}{warning_count} Warnings{NC}")
    print(f"{RED}{error_count} Failed tests{NC}")
    
    if error_count > 0:
        print("\nFailing tests:")
        for r in results:
            if r["status"] == "error":
                print(f" - {r['name']}: {r['message']}")
    
    # Generate recommendations
    print("\nRecommendations:")
    
    # Check for server not running
    if any(r["name"] == "API Connection" and r["status"] == "error" for r in results):
        print(" - Start the API server on port 8088 (./start.sh or run_vs_code_task 'Run API')")
    
    # Check for wrong port
    if any(r["name"] == "Wrong Port Check" and r["status"] == "warning" for r in results):
        print(" - API is running on the wrong port (8089). Fix port configuration")
        print("   (./fix_api_server_port.sh or run_vs_code_task 'Fix API Port Issues')")
    
    # Check for auth issues
    if any(r["name"] == "Authentication" and r["status"] == "error" for r in results):
        print(" - Authentication is failing. Check API logs and user credentials")
    
    # Check for frontend issues
    if any(r["name"] == "Frontend Server" and r["status"] == "error" for r in results):
        print(" - Start the frontend server (cd frontend && npm run dev)")
    
    # Save report to file
    report_file = f"api_diagnostic_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, "w") as f:
        f.write(f"API Diagnostic Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"=====================================================\n\n")
        
        for r in results:
            f.write(f"{r['name']}: {r['status'].upper()}\n")
            f.write(f"  {r['message']}\n")
            if r.get("details"):
                if isinstance(r["details"], dict) or isinstance(r["details"], list):
                    f.write(f"  {json.dumps(r['details'], indent=2)}\n")
                else:
                    f.write(f"  {r['details']}\n")
            f.write("\n")
    
    print(f"\nDetailed report saved to {report_file}")

def run_full_diagnostics():
    """Run all diagnostic tests and generate report."""
    print_header("Starting API Diagnostics")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # Test API on correct port
    connected_8088, data_8088 = test_api_connection(API_URL_8088)
    results.append({
        "name": "API Connection",
        "status": "success" if connected_8088 else "error",
        "message": "API is accessible on port 8088" if connected_8088 else "API is not accessible on port 8088",
        "details": data_8088 if connected_8088 else None
    })
    
    # Test API on wrong port
    connected_8089, data_8089 = test_api_connection(API_URL_8089)
    results.append({
        "name": "Wrong Port Check",
        "status": "warning" if connected_8089 else "success",
        "message": "API is running on incorrect port 8089" if connected_8089 else "No API running on port 8089 (correct)",
        "details": data_8089 if connected_8089 else None
    })
    
    # Test authentication
    auth_success, token = test_authentication()
    results.append({
        "name": "Authentication",
        "status": "success" if auth_success else "error",
        "message": "Authentication successful" if auth_success else "Authentication failed",
        "details": {"token_received": auth_success}
    })
    
    # Test protected endpoint
    if auth_success:
        protected_success = test_protected_endpoint(token)
        results.append({
            "name": "Protected Endpoint",
            "status": "success" if protected_success else "error",
            "message": "Successfully accessed protected endpoint" if protected_success else "Failed to access protected endpoint",
            "details": None
        })
        
        # Test companies endpoint
        companies_success = test_company_endpoint(token)
        results.append({
            "name": "Companies Endpoint",
            "status": "success" if companies_success else "error",
            "message": "Successfully accessed companies endpoint" if companies_success else "Failed to access companies endpoint",
            "details": None
        })
    
    # Test proxy bypass
    proxy_bypass_success = test_proxy_bypass()
    results.append({
        "name": "Proxy Bypass",
        "status": "success" if proxy_bypass_success else "warning",
        "message": "Successfully connected with proxy bypass" if proxy_bypass_success else "Failed to connect with proxy bypass",
        "details": None
    })
    
    # Check frontend server
    frontend_success = check_frontend_server()
    results.append({
        "name": "Frontend Server",
        "status": "success" if frontend_success else "error",
        "message": "Frontend server is running" if frontend_success else "Frontend server is not accessible",
        "details": None
    })
    
    # Generate report
    generate_report(results)

if __name__ == "__main__":
    run_full_diagnostics()
