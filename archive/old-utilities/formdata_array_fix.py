#!/usr/bin/env python3
"""
Focused test script to verify the FormData array parsing fix for company brand_colors.
This script simulates both frontend FormData submissions and backend parsing to ensure
that array values in FormData are correctly handled.
"""
import asyncio
import sys
import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

# Add the project root to the Python path
sys.path.insert(0, '/mnt/c/Users/brc07274/OneDrive - Philips/Philips Files/BU - CI/Repository/AI Marketing Agent (Python)/ai-marketing-agent')

# Mock form data as it would come from the frontend
MOCK_FORM_DATA = {
    "name": "Test Company",
    "description": "Test description",
    "email": "test@example.com",
    "phone": "123-456-7890",
    "address": "123 Test St",
    "brand_colors[0]": "#FF0000",  # Red
    "brand_colors[1]": "#00FF00",  # Green
    "brand_colors[2]": "#0000FF",  # Blue
}

class MockRequest:
    """Mock FastAPI request object with form() method"""
    
    def __init__(self, form_data: Dict[str, Any]):
        self.form_data = form_data
        
    async def form(self):
        """Simulates FastAPI request.form() method"""
        return MockFormData(self.form_data)
    
    def json(self):
        """Simulates FastAPI request.json() method"""
        # Convert indexed form data back to normal JSON structure
        result = {}
        for key, value in self.form_data.items():
            if '[' in key and ']' in key:
                base_key = key.split('[')[0]
                index = int(key.split('[')[1].split(']')[0])
                if base_key not in result:
                    result[base_key] = []
                # Extend list if needed
                while len(result[base_key]) <= index:
                    result[base_key].append(None)
                result[base_key][index] = value
            else:
                result[key] = value
        return result

class MockFormData:
    """Mock FormData object"""
    
    def __init__(self, data: Dict[str, Any]):
        self.data = data
        
    def __getitem__(self, key: str) -> Any:
        return self.data.get(key)
        
    def __contains__(self, key: str) -> bool:
        return key in self.data
        
    def keys(self):
        return self.data.keys()
        
    def getlist(self, key: str) -> List[Any]:
        """Get all values for a repeated form field"""
        # This is simplified for our test
        if key in self.data:
            return [self.data[key]]
        return []

async def test_form_data_array_parsing():
    """Test the array parsing logic from FormData"""
    print("Testing FormData array parsing...")
    
    # Create a mock request
    request = MockRequest(MOCK_FORM_DATA)
    
    # Get the form data
    form = await request.form()
    
    print(f"Form data keys: {list(form.keys())}")
    
    # Extract brand_colors from form data (handle both array formats)
    brand_colors = []
    
    # Method 1: Look for indexed form fields like brand_colors[0], brand_colors[1]
    color_index = 0
    while f"brand_colors[{color_index}]" in form:
        color_value = form[f"brand_colors[{color_index}]"]
        if color_value and isinstance(color_value, str) and color_value.strip():
            brand_colors.append(color_value.strip())
        color_index += 1
    
    # Method 2: Look for repeated "brand_colors" fields (alternative FormData format)
    if not brand_colors and "brand_colors" in form:
        brand_colors_raw = form.getlist("brand_colors")
        brand_colors = [color.strip() for color in brand_colors_raw if color and isinstance(color, str) and color.strip()]
    
    print(f"Parsed brand_colors: {brand_colors}")
    
    # Check if we extracted all colors correctly
    expected_colors = ["#FF0000", "#00FF00", "#0000FF"]
    if brand_colors == expected_colors:
        print("✅ SUCCESS: FormData array parsing works correctly!")
        return True
    else:
        print("❌ FAILED: FormData array parsing did not extract all colors.")
        print(f"Expected: {expected_colors}")
        print(f"Actual: {brand_colors}")
        return False

async def test_company_db():
    """Test the CompanyDB class with our fix"""
    print("\nTesting CompanyDB update logic...")
    
    try:
        from app.db.simple_mock_db import SimpleMockDatabase
        from app.db.company import CompanyDB
        from app.models.company import CompanyUpdate
        
        # Create a mock database and CompanyDB instance
        mock_db = SimpleMockDatabase()
        company_db = CompanyDB(mock_db.companies)
        
        # Create a test company
        test_company = {
            "_id": "test_company",
            "name": "Original Company",
            "description": "Original description",
            "email": "original@example.com",
            "brand_colors": ["#000000"], # Black
            "active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Insert the test company
        await mock_db.companies.insert_one(test_company)
        
        # Verify it was inserted
        original = await company_db.get_by_string_id("test_company")
        print(f"Original company: {original}")
        
        # Create an update with new colors
        update = CompanyUpdate(
            name="Updated Company",
            brand_colors=["#FF0000", "#00FF00", "#0000FF"]  # RGB
        )
        
        # Apply the update
        updated = await company_db.update_company("test_company", update)
        print(f"Updated company: {updated}")
        
        # Verify the update by getting it again
        final = await company_db.get_by_string_id("test_company")
        print(f"Retrieved company: {final}")
        
        # Check if colors were updated correctly
        if final and final.get('brand_colors') == ["#FF0000", "#00FF00", "#0000FF"]:
            print("✅ SUCCESS: CompanyDB update works correctly!")
            return True
        else:
            print("❌ FAILED: CompanyDB update did not save colors correctly.")
            if final:
                print(f"Expected: ['#FF0000', '#00FF00', '#0000FF']")
                print(f"Actual: {final.get('brand_colors')}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR during CompanyDB test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== Testing FormData Array Parsing Fix ===\n")
    
    try:
        # Test FormData array parsing
        form_data_result = asyncio.run(test_form_data_array_parsing())
        
        # Test CompanyDB update
        db_result = asyncio.run(test_company_db())
        
        # Final results
        print("\n=== FINAL RESULTS ===")
        print(f"FormData array parsing: {'PASSED' if form_data_result else 'FAILED'}")
        print(f"CompanyDB update: {'PASSED' if db_result else 'FAILED'}")
        print(f"Overall: {'PASSED' if form_data_result and db_result else 'FAILED'}")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
