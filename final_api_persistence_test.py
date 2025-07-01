#!/usr/bin/env python3
"""
Final verification test for brand colors persistence including AUTH token
"""
import sys
import asyncio
import json
from datetime import datetime

# Project path
PROJECT_PATH = '/mnt/c/Users/brc07274/OneDrive - Philips/Philips Files/BU - CI/Repository/AI Marketing Agent (Python)/ai-marketing-agent'

# Use development mock token
AUTH_TOKEN = "DEVELOPMENT_MOCK_TOKEN"

async def test_api_update_with_auth():
    """Test updating company via API with proper authentication"""
    print("=== COMPANY API UPDATE WITH AUTH TEST ===")
    
    try:
        # Import necessary modules
        sys.path.insert(0, PROJECT_PATH)
        import requests
        from app.models.company import CompanyUpdate
        
        # Step 1: Get current company
        print("\n1. Getting current company...")
        headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
        
        try:
            response = requests.get(
                "http://127.0.0.1:8088/api/v1/companies/active",
                headers=headers, 
                timeout=5
            )
            if response.status_code == 200:
                company = response.json()
                print(f"Current company: {company['name']}")
                print(f"Current colors: {company.get('brand_colors', [])}")
            else:
                print(f"Failed to get company: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except requests.exceptions.ConnectionError:
            print("API server not running - testing without API")
            # Test with direct database instead
            from app.db.simple_mock_db import SimpleMockDatabase
            from app.db.company import CompanyDB
            
            db = SimpleMockDatabase()
            company_db = CompanyDB(db.companies)
            
            # Create test company
            test_company = {
                "_id": "test_company",
                "name": "Original Company",
                "brand_colors": ["#000000"],
                "active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Insert directly into database
            await db.companies.insert_one(test_company)
            
            # Update company with new colors
            new_colors = ["#FF0000", "#00FF00", "#0000FF"]
            update_data = CompanyUpdate(
                name="Updated Company",
                brand_colors=new_colors
            )
            
            # Apply the update
            updated = await company_db.update_company("test_company", update_data)
            
            # Verify persistence
            final = await company_db.get_by_string_id("test_company")
            
            # Check results
            colors_updated = final.get('brand_colors') == new_colors
            print(f"Colors updated successfully: {'✓' if colors_updated else '✗'}")
            print(f"Final colors: {final.get('brand_colors')}")
            
            return colors_updated
        
        # Step 2: Update with new company details
        print("\n2. Updating company...")
        
        # New test colors
        new_colors = ["#FF5500", "#00FF55", "#5500FF"]
        
        # Prepare form data for update
        form_data = {
            "name": "Updated Test Company",
            "description": "Updated via final verification test"
        }
        
        # Add brand_colors as indexed form fields
        for i, color in enumerate(new_colors):
            form_data[f"brand_colors[{i}]"] = color
            
        # Send update request
        update_response = requests.put(
            f"http://127.0.0.1:8088/api/v1/companies/test_company",
            headers=headers,
            data=form_data,
            timeout=5
        )
        
        if update_response.status_code == 200:
            updated_company = update_response.json()
            print(f"Company updated: {updated_company['name']}")
            print(f"Updated colors: {updated_company.get('brand_colors', [])}")
        else:
            print(f"Failed to update company: {update_response.status_code}")
            print(f"Response: {update_response.text}")
            return False
            
        # Step 3: Verify changes persisted
        print("\n3. Verifying changes persisted...")
        verify_response = requests.get(
            "http://127.0.0.1:8088/api/v1/companies/active",
            headers=headers,
            timeout=5
        )
        
        if verify_response.status_code == 200:
            final_company = verify_response.json()
            print(f"Final company state: {json.dumps(final_company, indent=2)}")
            
            # Check if changes persisted
            name_updated = final_company.get('name') == "Updated Test Company"
            colors_updated = final_company.get('brand_colors') == new_colors
            
            print(f"Name updated: {'✓' if name_updated else '✗'}")
            print(f"Colors updated: {'✓' if colors_updated else '✗'}")
            print(f"Final colors: {final_company.get('brand_colors')}")
            
            # Overall result
            return name_updated and colors_updated
        else:
            print(f"Failed to verify persistence: {verify_response.status_code}")
            print(f"Response: {verify_response.text}")
            return False
            
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        # Run the test
        success = asyncio.run(test_api_update_with_auth())
        
        # Print final result
        print("\n" + "=" * 40)
        if success:
            print("✅ SUCCESS: Brand colors persist correctly!")
            print("Company information is properly saved and retrieved.")
            sys.exit(0)
        else:
            print("❌ FAILED: Brand colors persistence issue detected.")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
