#!/usr/bin/env python3

import requests
import json

# Set up a log file
log_file = "get_company_test.log"
with open(log_file, "w") as f:
    f.write("Starting GET company test...\n")

try:
    # Test the GET endpoint for company by ID
    with open(log_file, "a") as f:
        f.write("Getting company by ID...\n")
    
    response = requests.get("http://localhost:8088/api/v1/companies/test_company")
    
    with open(log_file, "a") as f:
        f.write(f"Status code: {response.status_code}\n")
        
    if response.status_code == 200:
        company = response.json()
        with open(log_file, "a") as f:
            f.write("Success! GET endpoint is working.\n")
            f.write(f"Company name: {company.get('name')}\n")
            f.write(f"Brand colors: {company.get('brand_colors')}\n")
            f.write(f"Full company data: {json.dumps(company, indent=2)}\n")
    else:
        with open(log_file, "a") as f:
            f.write(f"Failed: {response.text}\n")
except Exception as e:
    with open(log_file, "a") as f:
        f.write(f"Error: {str(e)}\n")

print(f"Test complete. Check {log_file} for results.")
