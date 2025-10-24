#!/usr/bin/env python3
"""
Regression tests to prevent the return of key issues:
1. AI providers count should always be 9
2. Database status page should be accessible without login redirect
3. Configure buttons should be functional

Run with: python tests/regression_tests.py
"""

import json
import time
import sys
import os
import urllib.request
import urllib.error
from typing import Dict, List, Any
from uuid import uuid4

class RegressionTester:
    def __init__(self, frontend_url: str = "http://localhost:3001", api_url: str = "http://localhost:8088"):
        self.frontend_url = frontend_url
        self.api_url = api_url
        self.correlation_id = f"test-{int(time.time())}"
        
    def make_request(self, url: str, method: str = "GET", headers: Dict[str, str] = None, timeout: int = 20) -> Dict[str, Any]:
        """Make HTTP request using urllib"""
        if headers is None:
            headers = {}
        
        # Add correlation ID
        headers['X-Correlation-ID'] = self.correlation_id
        headers['User-Agent'] = 'RegressionTester/1.0'
        
        try:
            req = urllib.request.Request(url, headers=headers, method=method)
            with urllib.request.urlopen(req, timeout=timeout) as response:
                status_code = response.getcode()
                data = response.read().decode('utf-8')
                
                try:
                    json_data = json.loads(data)
                except json.JSONDecodeError:
                    json_data = {"raw_response": data}
                
                return {
                    "status_code": status_code,
                    "data": json_data,
                    "headers": dict(response.headers),
                    "success": True
                }
        
        except urllib.error.HTTPError as e:
            return {
                "status_code": e.code,
                "data": {"error": e.reason},
                "headers": dict(e.headers) if hasattr(e, 'headers') else {},
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            return {
                "status_code": 0,
                "data": {"error": str(e)},
                "headers": {},
                "success": False,
                "error": str(e)
            }
        
    def test_api_providers_count(self) -> Dict[str, Any]:
        """Test that API returns exactly 9 AI providers"""
        print(f"[{self.correlation_id}] Testing API providers count...")
        
        try:
            # Test direct API access with correct endpoint
            response = self.make_request(f"{self.api_url}/api/v1/ai-providers")
            
            if response["status_code"] != 200:
                return {
                    "test": "api_providers_count",
                    "status": "FAIL",
                    "error": f"API returned status {response['status_code']}",
                    "details": response.get("data", {})
                }
            
            # The API returns a direct array, not {"providers": [...]}
            providers = response["data"]
            if isinstance(providers, list):
                provider_count = len(providers)
            else:
                provider_count = len(providers.get('providers', []))
            
            if provider_count != 9:
                return {
                    "test": "api_providers_count",
                    "status": "FAIL", 
                    "error": f"Expected 9 providers, got {provider_count}",
                    "providers": providers[:3] if isinstance(providers, list) else []  # Show first 3 for debugging
                }
                
            return {
                "test": "api_providers_count",
                "status": "PASS",
                "provider_count": provider_count,
                "providers": [p.get('name', 'Unknown') for p in providers] if isinstance(providers, list) else []
            }
            
        except Exception as e:
            return {
                "test": "api_providers_count", 
                "status": "ERROR",
                "error": str(e)
            }
    
    def test_proxy_providers_count(self) -> Dict[str, Any]:
        """Test that proxy route returns exactly 9 AI providers"""
        print(f"[{self.correlation_id}] Testing proxy providers count...")
        
        try:
            # Test via proxy - use the correct versioned endpoint that exists on backend
            response = self.make_request(f"{self.frontend_url}/api/v1/ai-providers")
            
            if response["status_code"] != 200:
                return {
                    "test": "proxy_providers_count",
                    "status": "FAIL",
                    "error": f"Proxy returned status {response['status_code']}",
                    "details": response.get("data", {})
                }
            
            # Handle both direct array and object with providers key
            providers = response["data"]
            if isinstance(providers, list):
                provider_count = len(providers)
            else:
                provider_count = len(providers.get('providers', []))
            
            if provider_count != 9:
                return {
                    "test": "proxy_providers_count",
                    "status": "FAIL",
                    "error": f"Expected 9 providers via proxy, got {provider_count}",
                    "providers": providers[:3] if isinstance(providers, list) else []
                }
                
            return {
                "test": "proxy_providers_count",
                "status": "PASS",
                "provider_count": provider_count,
                "providers": [p.get('name', 'Unknown') for p in providers] if isinstance(providers, list) else []
            }
            
        except Exception as e:
            return {
                "test": "proxy_providers_count",
                "status": "ERROR", 
                "error": str(e)
            }
    
    def test_database_status_accessibility(self) -> Dict[str, Any]:
        """Test that database status page is accessible without login redirect"""
        print(f"[{self.correlation_id}] Testing database status page accessibility...")
        
        try:
            # Test database status page - use longer timeout for Next.js compilation
            response = self.make_request(f"{self.frontend_url}/en/database-status", timeout=30)
            
            # Check for successful page load
            if response["status_code"] == 200:
                return {
                    "test": "database_status_accessibility", 
                    "status": "PASS",
                    "page_status": response["status_code"]
                }
            elif response["status_code"] in [301, 302, 303, 307, 308]:
                location = response.get("headers", {}).get("location", "")
                if 'login' in location.lower():
                    return {
                        "test": "database_status_accessibility",
                        "status": "FAIL",
                        "error": f"Page redirects to login: {location}",
                        "redirect_status": response["status_code"]
                    }
                else:
                    return {
                        "test": "database_status_accessibility",
                        "status": "WARNING",
                        "error": f"Page redirects to: {location}",
                        "redirect_status": response["status_code"]
                    }
            else:
                return {
                    "test": "database_status_accessibility",
                    "status": "FAIL",
                    "error": f"Page returned status {response['status_code']}",
                    "details": str(response.get("data", {}))[:500]
                }
                
        except Exception as e:
            return {
                "test": "database_status_accessibility",
                "status": "ERROR",
                "error": str(e)
            }
    
    def test_ai_providers_page_load(self) -> Dict[str, Any]:
        """Test that AI providers page loads without infinite spinner"""
        print(f"[{self.correlation_id}] Testing AI providers page load...")
        
        try:
            response = self.make_request(f"{self.frontend_url}/en/ai-providers", timeout=30)
            
            if response["status_code"] == 200:
                # Check for basic page structure (not a redirect to login)
                content = str(response.get("data", {}))
                
                # Look for signs of proper page load vs infinite loading
                has_providers_content = 'ai-providers' in content.lower() or 'configure' in content.lower()
                has_error_indicators = 'error' in content.lower() and 'loading' in content.lower()
                
                return {
                    "test": "ai_providers_page_load",
                    "status": "PASS" if has_providers_content and not has_error_indicators else "WARNING",
                    "page_status": response["status_code"],
                    "has_providers_content": has_providers_content,
                    "potential_loading_issues": has_error_indicators
                }
            else:
                return {
                    "test": "ai_providers_page_load",
                    "status": "FAIL",
                    "error": f"Page returned status {response['status_code']}",
                    "details": str(response.get("data", {}))[:500]
                }
                
        except Exception as e:
            return {
                "test": "ai_providers_page_load",
                "status": "ERROR",
                "error": str(e)
            }
    
    def test_correlation_id_tracking(self) -> Dict[str, Any]:
        """Test that correlation IDs are properly tracked in logs"""
        print(f"[{self.correlation_id}] Testing correlation ID tracking...")
        
        try:
            # Make a request and check if correlation ID comes back
            response = self.make_request(f"{self.api_url}/api/v1/ai-providers")
            
            # Check for correlation ID in headers (case-insensitive)
            headers = response.get("headers", {})
            returned_correlation_id = None
            
            # Try different header case variations
            for header_name in headers:
                if header_name.lower() == 'x-correlation-id':
                    returned_correlation_id = headers[header_name]
                    break
            
            if returned_correlation_id == self.correlation_id:
                return {
                    "test": "correlation_id_tracking",
                    "status": "PASS",
                    "sent_correlation_id": self.correlation_id,
                    "returned_correlation_id": returned_correlation_id
                }
            else:
                return {
                    "test": "correlation_id_tracking",
                    "status": "FAIL",
                    "error": "Correlation ID not properly returned",
                    "sent_correlation_id": self.correlation_id,
                    "returned_correlation_id": returned_correlation_id,
                    "available_headers": list(headers.keys())
                }
                
        except Exception as e:
            return {
                "test": "correlation_id_tracking",
                "status": "ERROR",
                "error": str(e)
            }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all regression tests and return summary"""
        print(f"\n=== Starting Regression Tests [{self.correlation_id}] ===\n")
        
        tests = [
            self.test_api_providers_count,
            self.test_proxy_providers_count, 
            self.test_database_status_accessibility,
            self.test_ai_providers_page_load,
            self.test_correlation_id_tracking
        ]
        
        results = []
        passed = 0
        failed = 0
        errors = 0
        warnings = 0
        
        for test_func in tests:
            result = test_func()
            results.append(result)
            
            status = result['status']
            test_name = result['test']
            
            if status == 'PASS':
                passed += 1
                print(f"✅ {test_name}: PASSED")
            elif status == 'FAIL':
                failed += 1
                print(f"❌ {test_name}: FAILED - {result.get('error', 'Unknown error')}")
            elif status == 'WARNING':
                warnings += 1
                print(f"⚠️  {test_name}: WARNING - {result.get('error', 'Potential issue')}")
            else:  # ERROR
                errors += 1
                print(f"💥 {test_name}: ERROR - {result.get('error', 'Unknown error')}")
        
        summary = {
            "correlation_id": self.correlation_id,
            "timestamp": time.time(),
            "total_tests": len(tests),
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "warnings": warnings,
            "results": results
        }
        
        print(f"\n=== Test Summary [{self.correlation_id}] ===")
        print(f"Total Tests: {len(tests)}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Errors: {errors}")
        print(f"Warnings: {warnings}")
        
        if failed > 0 or errors > 0:
            print("\n🚨 REGRESSION DETECTED - Some tests failed!")
            return summary
        elif warnings > 0:
            print("\n⚠️  All tests passed but there are warnings to review.")
            return summary
        else:
            print("\n✅ All regression tests passed!")
            return summary

def main():
    """Main entry point for regression testing"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help":
            print("Usage: python tests/regression_tests.py [frontend_url] [api_url]")
            print("Defaults: frontend_url=http://localhost:3001, api_url=http://localhost:8088")
            return
        
        frontend_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:3001"
        api_url = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:8088"
    else:
        frontend_url = "http://localhost:3001"
        api_url = "http://localhost:8088"
    
    tester = RegressionTester(frontend_url, api_url)
    summary = tester.run_all_tests()
    
    # Save results to file
    results_file = f"test_results_{int(time.time())}.json"
    with open(results_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\nResults saved to: {results_file}")
    
    # Exit with error code if tests failed
    if summary['failed'] > 0 or summary['errors'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()