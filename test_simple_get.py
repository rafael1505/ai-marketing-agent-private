import requests

def test_get():
    base_url = "http://127.0.0.1:8088"
    
    # Get current company from API
    print("Getting company from API...")
    response = requests.get(f"{base_url}/api/v1/companies/active", 
                          proxies={"http": None, "https": None})
    
    if response.status_code == 200:
        company = response.json()
        print(f"Company name: {company['name']}")
        print(f"Company ID: {company.get('id')}")
        print(f"Internal _id: {company.get('_id')}")
        print(f"Brand colors: {company.get('brand_colors')}")
        return True
    else:
        print(f"Failed: {response.status_code}")
        print(response.text)
        return False

if __name__ == "__main__":
    test_get()
