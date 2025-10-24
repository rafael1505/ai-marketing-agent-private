#!/usr/bin/env python3
"""
Comprehensive authentication test script for the AI Marketing Agent
Tests both JSON authentication and FormData authentication
"""
import requests
import json
import os
import sys
from datetime import datetime

# API configuration
API_BASE = "http://127.0.0.1:8089/api/v1"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpassword"

class AuthTester:
    def __init__(self):
        self.token = None
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "total": 0
        }
        self.create_test_files()
        
    def create_test_files(self):
        # Create test files for uploads
        with open("test_file.txt", "w") as f:
            f.write(f"Test file content generated at {datetime.now()}")
        print("Created test files for upload testing")
    
    def cleanup(self):
        # Remove test files
        if os.path.exists("test_file.txt"):
            os.remove("test_file.txt")
        print("Cleaned up test files")
    
    def print_separator(self):
        print("\n" + "=" * 50 + "\n")
    
    def log_result(self, test_name, passed, message=None):
        self.test_results["total"] += 1
        
        if passed:
            self.test_results["passed"] += 1
            status = "✓ PASSED"
            color = "\033[92m"  # Green
        else:
            self.test_results["failed"] += 1
            status = "✗ FAILED"
            color = "\033[91m"  # Red
            
        reset = "\033[0m"
        
        print(f"{color}{status}{reset}: {test_name}")
        if message:
            print(f"  {message}")
    
    def get_auth_token(self):
        print("Testing login to get authentication token...")
        
        try:
            # Try /auth/login endpoint
            login_url = f"{API_BASE}/auth/login"
            login_data = {"username": TEST_EMAIL, "password": TEST_PASSWORD}
            
            print(f"POST {login_url}")
            response = requests.post(login_url, data=login_data)
            
            if response.status_code != 200:
                # Try /auth/token endpoint as fallback
                login_url = f"{API_BASE}/auth/token"
                print(f"Fallback: POST {login_url}")
                response = requests.post(login_url, data=login_data)
            
            if response.status_code == 200:
                token_data = response.json()
                self.token = token_data.get('access_token')
                self.log_result("Authentication token retrieval", True, 
                                f"Token: {self.token[:15]}...")
                return True
            else:
                self.log_result("Authentication token retrieval", False, 
                                f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_result("Authentication token retrieval", False, 
                          f"Exception: {str(e)}")
            return False
            
    def test_json_auth(self):
        print("Testing JSON request with authentication...")
        
        if not self.token:
            self.log_result("JSON authentication test", False, 
                          "No authentication token available")
            return False
        
        try:
            # Use the test JSON endpoint
            test_url = f"{API_BASE}/auth-test/test-json"
            headers = {"Authorization": f"Bearer {self.token}"}
            test_data = {"test": True, "message": "Testing JSON authentication"}
            
            print(f"POST {test_url}")
            response = requests.post(test_url, json=test_data, headers=headers)
            
            if response.status_code == 200:
                self.log_result("JSON authentication test", True, 
                              f"Response: {json.dumps(response.json(), indent=2)[:100]}...")
                return True
            else:
                self.log_result("JSON authentication test", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_result("JSON authentication test", False, 
                          f"Exception: {str(e)}")
            return False
    
    def test_formdata_auth(self):
        print("Testing FormData request with authentication...")
        
        if not self.token:
            self.log_result("FormData authentication test", False, 
                          "No authentication token available")
            return False
            
        try:
            # Use the special FormData test endpoint
            test_url = f"{API_BASE}/auth-test/test-form-special"
            headers = {"Authorization": f"Bearer {self.token}"}
            
            # Create the multipart form data
            files = {
                "test_file": ("test_file.txt", open("test_file.txt", "rb"), "text/plain")
            }
            form_data = {
                "test_field": "Test value for FormData authentication"
            }
            
            print(f"POST {test_url}")
            response = requests.post(
                test_url, 
                headers=headers,
                files=files,
                data=form_data
            )
            
            if response.status_code == 200:
                self.log_result("FormData authentication test", True, 
                              f"Response: {json.dumps(response.json(), indent=2)[:100]}...")
                return True
            else:
                self.log_result("FormData authentication test", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_result("FormData authentication test", False, 
                          f"Exception: {str(e)}")
            return False
    
    def test_company_update(self):
        print("Testing company update with FormData...")
        
        if not self.token:
            self.log_result("Company update test", False, 
                          "No authentication token available")
            return False
            
        try:
            # Use the company update endpoint
            company_url = f"{API_BASE}/companies/test_company"
            headers = {"Authorization": f"Bearer {self.token}"}
            
            # Create the multipart form data
            files = {
                "logo_file": ("test_file.txt", open("test_file.txt", "rb"), "text/plain")
            }
            company_data = {
                "name": f"Test Company (Updated {datetime.now().strftime('%H:%M:%S')})",
                "description": "Updated via the comprehensive test script",
                "email": "test@example.com",
                "phone": "555-TEST"
            }
            
            print(f"PUT {company_url}")
            response = requests.put(
                company_url, 
                headers=headers,
                files=files,
                data=company_data
            )
            
            if response.status_code == 200:
                self.log_result("Company update test", True, 
                              f"Response: {json.dumps(response.json(), indent=2)[:100]}...")
                return True
            else:
                self.log_result("Company update test", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_result("Company update test", False, 
                          f"Exception: {str(e)}")
            return False
    
    def test_headers_debug(self):
        print("Testing authentication headers debugging...")
        
        if not self.token:
            self.log_result("Headers debug test", False, 
                          "No authentication token available")
            return False
            
        try:
            # Use the auth debug endpoint
            debug_url = f"{API_BASE}/auth-test/auth-debug"
            headers = {"Authorization": f"Bearer {self.token}"}
            
            print(f"GET {debug_url}")
            response = requests.get(debug_url, headers=headers)
            
            if response.status_code == 200:
                self.log_result("Headers debug test", True, 
                              f"Response: {json.dumps(response.json(), indent=2)[:100]}...")
                return True
            else:
                self.log_result("Headers debug test", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_result("Headers debug test", False, 
                          f"Exception: {str(e)}")
            return False
    
    def print_summary(self):
        self.print_separator()
        print("TEST SUMMARY")
        print("-" * 20)
        print(f"Total tests: {self.test_results['total']}")
        print(f"Passed: {self.test_results['passed']}")
        print(f"Failed: {self.test_results['failed']}")
        
        if self.test_results['failed'] == 0:
            print("\n\033[92m✓ All authentication tests passed!\033[0m")
            print("The authentication fixes are working correctly.")
        else:
            print(f"\n\033[91m✗ {self.test_results['failed']} tests failed.\033[0m")
            print("Further investigation is needed.")
        
        self.print_separator()
    
    def run_all_tests(self):
        self.print_separator()
        print("COMPREHENSIVE AUTHENTICATION TEST")
        print("Testing all authentication mechanisms for AI Marketing Agent")
        self.print_separator()
        
        # Get authentication token first
        if self.get_auth_token():
            # Run all the tests
            self.test_json_auth()
            self.test_formdata_auth() 
            self.test_company_update()
            self.test_headers_debug()
        else:
            print("Cannot continue tests without authentication token")
            
        self.print_summary()
        self.cleanup()
        
        return self.test_results['failed'] == 0

def main():
    tester = AuthTester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
