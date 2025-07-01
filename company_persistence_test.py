#!/usr/bin/env python3

"""
Comprehensive test script for company data persistence issues
This script:
1. Authenticates with the API (or uses mock token for testing)
2. Gets the current company info
3. Updates the company with new brand colors
4. Verifies the changes were persisted
"""

import requests
import json
import time
import os
import sys

def test_company_persistence():
    base_url = "http://127.0.0.1:8088"
    # Mock token for development environment
    mock_token = "DEVELOPMENT_MOCK_TOKEN_FOR_TESTING"
    
    print("\n🔍 COMPANY PERSISTENCE TEST\n" + "="*30)
    
    # Step 1: Get current company
    print("\n📋 Step 1: Getting current company info...")
    try:
        print("  Sending GET request to API...")
        # Add a 5 second timeout to avoid hanging indefinitely
        response = requests.get(
            f"{base_url}/api/v1/companies/active", 
            headers={"Authorization": f"Bearer {mock_token}"},
            proxies={"http": None, "https": None},
            timeout=5  # Add 5 second timeout
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to get company: {response.status_code}")
            print(response.text)
            return False
        
        # Debug response
        print(f"🔍 Response status: {response.status_code}")
        print(f"🔍 Response headers: {response.headers}")
        
        # Get raw text first to debug
        raw_text = response.text
        print(f"🔍 Raw response (first 200 chars): {raw_text[:200]}...")
        
        try:
            # Try to parse as JSON with error handling
            company = response.json()
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse JSON response: {e}")
            # Try to fix common issues with the response
            fixed_text = raw_text.strip()
            try:
                company = json.loads(fixed_text)
                print("✅ Successfully parsed JSON after fixing")
            except:
                print("❌ Could not parse response as JSON even after fixing")
                return False
        
        # Verify required fields exist and have reasonable values
        if not isinstance(company, dict):
            print(f"❌ Company is not a dictionary: {type(company)}")
            return False
            
        if 'name' not in company:
            print("❌ Company name is missing from response")
            # Use a default company for testing purposes
            company = {
                'id': 'test_company',
                'name': 'Default Test Company',
                'description': 'Default description for testing',
                'brand_colors': []
            }
            print("⚠️ Using default company data for testing")
        else:
            print(f"✅ Found company: {company['name']}")
            print(f"📝 Current data:")
            print(f"   - ID: {company.get('id', 'N/A')}")
            print(f"   - _id: {company.get('_id', 'N/A')}")
            print(f"   - Colors: {company.get('brand_colors', [])}")
        
        company_id = company.get('id', 'test_company')
        
    except requests.exceptions.Timeout:
        print(f"❌ API request timed out after 5 seconds. The server might be hanging.")
        return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection error. The API server might not be running.")
        return False
    except Exception as e:
        print(f"❌ Error getting company: {str(e)}")
        return False
    
    # Generate unique test values
    test_name = f"Test Company {time.time():.0f}"
    test_colors = [f"#{time.time():.0f}"[:7], "#00FF00"]
    
    print(f"\n📋 Step 2: Updating company with test data...")
    print(f"   - Test name: {test_name}")
    print(f"   - Test colors: {test_colors}")
    
    # Step 2: Update company using FormData (similar to frontend)
    form_data = {
        'name': test_name,
        'description': company.get('description', 'Test Description'),
        'email': company.get('email', ''),
        'phone': company.get('phone', ''),
        'address': company.get('address', ''),
        'logo_url': company.get('logo_url', ''),
    }
    
    # Try different ways to send colors
    # First, try direct array
    form_data['brand_colors'] = test_colors
    
    # Also add in indexed format like the frontend does
    for i, color in enumerate(test_colors):
        form_data[f'brand_colors[{i}]'] = color
    
    try:
        print("  Sending PUT request to API...")
        response = requests.put(
            f"{base_url}/api/v1/companies/{company_id}",
            data=form_data,
            headers={"Authorization": f"Bearer {mock_token}"},
            proxies={"http": None, "https": None},
            timeout=5  # Add 5 second timeout
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to update company: {response.status_code}")
            print(response.text)
            return False
        
        try:
            updated_company = response.json()
            print(f"✅ Company updated successfully")
            print(f"📝 Response data:")
            print(f"   - Name: {updated_company.get('name', 'Unknown')}")
            print(f"   - Colors: {updated_company.get('brand_colors', [])}")
        except json.JSONDecodeError as e:
            print(f"⚠️ Warning: Could not parse update response as JSON: {e}")
            # Continue with testing anyway using the request data
            updated_company = {
                'name': test_name,
                'brand_colors': test_colors
            }
            print("⚠️ Using request data for testing continuation")
        
    except Exception as e:
        print(f"❌ Error updating company: {str(e)}")
        return False
    
    # Wait a moment to ensure changes are persisted
    print("\n⏳ Waiting 2 seconds to ensure persistence...")
    time.sleep(2)
    
    # Step 3: Get company again to verify persistence
    print("\n📋 Step 3: Verifying data persistence...")
    try:
        print("  Sending GET request to API...")
        response = requests.get(
            f"{base_url}/api/v1/companies/active", 
            headers={"Authorization": f"Bearer {mock_token}"},
            proxies={"http": None, "https": None},
            timeout=5  # Add 5 second timeout
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to get company again: {response.status_code}")
            print(response.text)
            return False
        
        try:
            final_company = response.json()
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse final response as JSON: {e}")
            print(f"🔍 Raw response (first 200 chars): {response.text[:200]}...")
            return False
        
        # Verify required fields
        if 'name' not in final_company:
            print("❌ Final company name is missing from response")
            return False
            
        print(f"✅ Retrieved company: {final_company['name']}")
        print(f"📝 Final data:")
        print(f"   - ID: {final_company.get('id', 'N/A')}")
        print(f"   - _id: {final_company.get('_id', 'N/A')}")
        print(f"   - Colors: {final_company.get('brand_colors', [])}")
        
        # Verify persistence
        name_persisted = final_company['name'] == test_name
        colors_persisted = sorted(final_company.get('brand_colors', [])) == sorted(test_colors)
        
        print(f"\n🔍 PERSISTENCE VERIFICATION:")
        print(f"   - Name persisted: {'✅' if name_persisted else '❌'}")
        print(f"   - Colors persisted: {'✅' if colors_persisted else '❌'}")
        print(f"   - Expected colors: {test_colors}")
        print(f"   - Actual colors: {final_company.get('brand_colors', [])}")
        
        if name_persisted and colors_persisted:
            print("\n✅ SUCCESS: All changes persisted correctly!")
            return True
        else:
            print("\n❌ FAILURE: Some changes did not persist.")
            return False
        
    except Exception as e:
        print(f"❌ Error verifying persistence: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_company_persistence()
    sys.exit(0 if success else 1)
