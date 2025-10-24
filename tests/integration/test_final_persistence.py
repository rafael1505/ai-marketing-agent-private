#!/usr/bin/env python3
"""
Test company persistence with new values to confirm fix
"""
import requests
import time

API_BASE_URL = "http://127.0.0.1:8088/api/v1"
DEV_TOKEN = "DEVELOPMENT_MOCK_TOKEN_FOR_TESTING"

def test_new_persistence():
    """Test persistence with completely new values"""
    print("🧪 Testing Company Persistence with NEW VALUES")
    print("=" * 50)
    
    # Get current state
    response = requests.get(f"{API_BASE_URL}/companies/active")
    current = response.json()
    print(f"Current: {current['name']}")
    print(f"Current colors: {current.get('brand_colors', [])}")
    
    # Update with NEW values
    print("\n🔄 Updating with COMPLETELY NEW values...")
    headers = {"Authorization": f"Bearer {DEV_TOKEN}"}
    
    new_data = {
        "name": "FINAL TEST Company NEW",
        "description": "FINAL persistence test",
        "email": "final.test@example.com",
        "phone": "+1-555-FINAL-TEST",
        "address": "456 Final Test Avenue",
        "brand_colors[0]": "#AABBCC",  # New colors
        "brand_colors[1]": "#DDEEFF", 
        "brand_colors[2]": "#998877",
    }
    
    response = requests.put(f"{API_BASE_URL}/companies/test_company", headers=headers, data=new_data)
    print(f"Update status: {response.status_code}")
    
    if response.status_code == 200:
        updated = response.json()
        print(f"✅ Updated to: {updated['name']}")
        print(f"✅ New colors: {updated.get('brand_colors', [])}")
        
        # Wait and verify persistence
        print("\n⏳ Waiting 2 seconds...")
        time.sleep(2)
        
        response = requests.get(f"{API_BASE_URL}/companies/active")
        final = response.json()
        print(f"\n🔍 FINAL VERIFICATION:")
        print(f"Name: {final['name']}")
        print(f"Colors: {final.get('brand_colors', [])}")
        print(f"Email: {final.get('email', 'None')}")
        
        # Check if changes persisted
        name_match = final['name'] == "FINAL TEST Company NEW"
        colors_match = final.get('brand_colors', []) == ["#AABBCC", "#DDEEFF", "#998877"]
        email_match = final.get('email') == "final.test@example.com"
        
        print(f"\n🎯 RESULTS:")
        print(f"Name persisted: {'✅' if name_match else '❌'}")
        print(f"Colors persisted: {'✅' if colors_match else '❌'}")  
        print(f"Email persisted: {'✅' if email_match else '❌'}")
        
        if name_match and colors_match and email_match:
            print(f"\n🎉 SUCCESS: Company persistence is FULLY WORKING!")
            return True
        else:
            print(f"\n❌ FAILURE: Some data not persisting")
            return False
    else:
        print(f"❌ Update failed: {response.text}")
        return False

if __name__ == "__main__":
    test_new_persistence()
