#!/usr/bin/env python3

import requests

def test_company_by_id():
    base_url = "http://127.0.0.1:8088"
    company_id = "test_company"
    
    print(f"Testing direct company endpoint for ID: {company_id}")
    
    response = requests.get(f"{base_url}/api/v1/companies/{company_id}",
                           proxies={"http": None, "https": None})
    
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        print("Success! Company data retrieved:")
        company = response.json()
        print(f"Name: {company['name']}")
        print(f"Brand Colors: {company.get('brand_colors', [])}")
    else:
        print(f"Failed: {response.text}")

if __name__ == "__main__":
    test_company_by_id()
