#!/usr/bin/env python3
"""
Simple script to send a company update request with different content types
"""

import requests
import json
import argparse

def test_json_request(base_url="http://127.0.0.1:8088"):
    """Test updating company with JSON content type"""
    url = f"{base_url}/api/v1/companies/test_company"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzUwODU3ODc2fQ.LG-EpDaoAgH0ih_Weo0p50qo8c3YXT-ZKtOT-W2GD8Q"
    
    data = {
        "name": "JSON Test Company",
        "description": "Updated via JSON request",
        "brand_colors": ["#FF0000", "#00FF00"]
    }
    
    print(f"\nSending JSON request to {url}")
    response = requests.put(
        url,
        json=data,
        headers={"Authorization": f"Bearer {token}"},
        proxies={"http": None, "https": None}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:1000]}")
    
    # Check if changes were persisted
    if response.status_code == 200:
        verify_response = requests.get(
            f"{base_url}/api/v1/companies/active",
            proxies={"http": None, "https": None}
        )
        
        if verify_response.status_code == 200:
            company = verify_response.json()
            print(f"\nVerification:")
            print(f"Company name: {company.get('name')}")
            print(f"Brand colors: {company.get('brand_colors')}")

def test_form_request(base_url="http://127.0.0.1:8088"):
    """Test updating company with form data"""
    url = f"{base_url}/api/v1/companies/test_company"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzUwODU3ODc2fQ.LG-EpDaoAgH0ih_Weo0p50qo8c3YXT-ZKtOT-W2GD8Q"
    
    data = {
        "name": "FormData Test Company",
        "description": "Updated via form request",
        "brand_colors": json.dumps(["#0000FF", "#FFFF00"])
    }
    
    print(f"\nSending form request to {url}")
    response = requests.put(
        url,
        data=data,
        headers={"Authorization": f"Bearer {token}"},
        proxies={"http": None, "https": None}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:1000]}")
    
    # Check if changes were persisted
    if response.status_code == 200:
        verify_response = requests.get(
            f"{base_url}/api/v1/companies/active",
            proxies={"http": None, "https": None}
        )
        
        if verify_response.status_code == 200:
            company = verify_response.json()
            print(f"\nVerification:")
            print(f"Company name: {company.get('name')}")
            print(f"Brand colors: {company.get('brand_colors')}")

def test_indexed_form_request(base_url="http://127.0.0.1:8088"):
    """Test updating company with indexed form data"""
    url = f"{base_url}/api/v1/companies/test_company"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzUwODU3ODc2fQ.LG-EpDaoAgH0ih_Weo0p50qo8c3YXT-ZKtOT-W2GD8Q"
    
    data = {
        "name": "Indexed FormData Test",
        "description": "Updated via indexed form fields",
        "brand_colors[0]": "#AA00FF",
        "brand_colors[1]": "#00FFAA"
    }
    
    print(f"\nSending indexed form request to {url}")
    response = requests.put(
        url,
        data=data,
        headers={"Authorization": f"Bearer {token}"},
        proxies={"http": None, "https": None}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:1000]}")
    
    # Check if changes were persisted
    if response.status_code == 200:
        verify_response = requests.get(
            f"{base_url}/api/v1/companies/active",
            proxies={"http": None, "https": None}
        )
        
        if verify_response.status_code == 200:
            company = verify_response.json()
            print(f"\nVerification:")
            print(f"Company name: {company.get('name')}")
            print(f"Brand colors: {company.get('brand_colors')}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test company update with different request types")
    parser.add_argument("--url", default="http://127.0.0.1:8088", help="Base URL for the API")
    parser.add_argument("--test", choices=["json", "form", "indexed", "all"], default="all", help="Test type to run")
    args = parser.parse_args()
    
    # Run the specified test
    if args.test == "json" or args.test == "all":
        test_json_request(args.url)
    
    if args.test == "form" or args.test == "all":
        test_form_request(args.url)
    
    if args.test == "indexed" or args.test == "all":
        test_indexed_form_request(args.url)
