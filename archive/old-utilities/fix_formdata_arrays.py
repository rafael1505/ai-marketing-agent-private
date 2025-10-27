#!/usr/bin/env python3

"""
This script adds a debug endpoint to verify FormData array handling.
Run this script to add the debug endpoint to the API server.
"""

import os
import sys
import re
from typing import List, Dict, Any, Optional

def patch_companies_file():
    """
    Updates the companies.py file to fix the FormData array handling issue
    """
    companies_file = os.path.join('app', 'api', 'v1', 'companies.py')
    
    try:
        with open(companies_file, 'r') as file:
            content = file.read()
        
        # Add brand_colors parameter to update_company function
        pattern = r'@router\.put\("/{company_id}", response_model=None\).*?\nasync def update_company\('
        pattern += r'[^)]*?'  # Match all parameters
        pattern += r'logo_file: Optional\[UploadFile\] = File\(None\)'
        pattern += r'\s*\) -> Any:'
        
        replacement = '@router.put("/{company_id}", response_model=None)  # Remove response_model to skip validation\n'
        replacement += 'async def update_company(\n'
        replacement += '    company_id: str,\n'
        replacement += '    request: Request,\n'
        replacement += '    current_user: dict = Depends(get_admin_user_formdata),  # Use our special FormData auth dependency\n'
        replacement += '    content_type: str = Header(None),\n'
        replacement += '    name: Optional[str] = Form(None),\n'
        replacement += '    description: Optional[str] = Form(None),\n'
        replacement += '    email: Optional[str] = Form(None),\n'
        replacement += '    phone: Optional[str] = Form(None),\n'
        replacement += '    address: Optional[str] = Form(None),\n'
        replacement += '    logo_url: Optional[str] = Form(None),\n'
        replacement += '    logo_file: Optional[UploadFile] = File(None),\n'
        replacement += '    # Add explicit brand_colors parameter\n'
        replacement += '    brand_colors: Optional[List[str]] = None\n'
        replacement += ') -> Any:'
        
        # Apply regex replacement with re.DOTALL to match across lines
        updated_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
        # Modify the brand_colors handling in the function
        brand_colors_section = r"# If middleware didn't work, parse them manually\s*"
        brand_colors_section += r"if 'brand_colors' in parsed_arrays:.*?"
        brand_colors_section += r"logger\.info\(f\"Final brand_colors: {brand_colors}\"\)"
        
        brand_colors_replacement = """# If brand_colors was passed as a parameter, use it first
            if brand_colors:
                logger.info(f"Using brand_colors from parameter: {brand_colors}")
            # If middleware found arrays, use those next
            elif 'brand_colors' in parsed_arrays:
                brand_colors = parsed_arrays['brand_colors']
                logger.info(f"Found parsed brand_colors from middleware: {brand_colors}")
            elif 'brand_colors' in form:
                # Try to parse as JSON string
                import json
                try:
                    brand_colors_str = form.get('brand_colors')
                    logger.info(f"Attempting to parse brand_colors as JSON: {brand_colors_str}")
                    brand_colors = json.loads(brand_colors_str)
                    logger.info(f"Successfully parsed brand_colors as JSON: {brand_colors}")
                except json.JSONDecodeError:
                    brand_colors_value = form.get('brand_colors')
                    if isinstance(brand_colors_value, str):
                        # Split by comma if it's a comma-separated string
                        brand_colors = [c.strip() for c in brand_colors_value.split(',') if c.strip()]
                        logger.info(f"Parsed brand_colors as comma-separated string: {brand_colors}")
                    else:
                        brand_colors = [brand_colors_value]
                        logger.info(f"Using brand_colors as single value: {brand_colors}")
            else:
                # Fallback to manual indexed array extraction
                logger.info("Falling back to manual brand_colors extraction")
                color_index = 0
                while f"brand_colors[{color_index}]" in form:
                    color_value = form[f"brand_colors[{color_index}]"]
                    if color_value and str(color_value).strip():
                        brand_colors.append(str(color_value).strip())
                    color_index += 1
                
            logger.info(f"Final brand_colors: {brand_colors}")"""
        
        # Apply this replacement as well
        updated_content = re.sub(brand_colors_section, brand_colors_replacement, updated_content, flags=re.DOTALL)
        
        # Also add a debug endpoint to the end of the file
        debug_endpoint = """

@router.post("/debug-formdata", response_model=Dict[str, Any])
async def debug_formdata(
    request: Request,
    content_type: str = Header(None),
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    logo_file: Optional[UploadFile] = File(None)
) -> Any:
    \"\"\"
    Debug endpoint to troubleshoot FormData array handling
    \"\"\"
    logger.info("Processing FormData debug request")
    logger.info(f"Content-Type: {content_type}")
    
    try:
        form = await request.form()
        logger.info(f"Form data keys: {list(form.keys())}")
        
        # Extract all form values including arrays
        form_data = {}
        for key in form.keys():
            # Extract array indices if present
            array_match = re.match(r'([^\[]+)\[(\d+)\]', key)
            if array_match:
                base_name, index = array_match.group(1), int(array_match.group(2))
                if base_name not in form_data:
                    form_data[base_name] = []
                # Extend the list if needed
                while len(form_data[base_name]) <= index:
                    form_data[base_name].append(None)
                form_data[base_name][index] = form[key]
            else:
                form_data[key] = form[key]
        
        # Try to get parsed arrays from middleware
        parsed_arrays = await get_parsed_form_arrays(request)
        logger.info(f"Parsed arrays from middleware: {parsed_arrays}")
        
        # Combine the results
        result = {
            "request_content_type": content_type,
            "form_params": {
                "name": name,
                "description": description,
                "file_info": {
                    "filename": logo_file.filename if logo_file else None,
                    "content_type": logo_file.content_type if logo_file else None
                } if logo_file else None
            },
            "parsed_form": form_data,
            "parsed_arrays": parsed_arrays,
            "raw_keys": list(form.keys())
        }
        
        return result
    except Exception as e:
        logger.error(f"Error in debug endpoint: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Debug error: {str(e)}")
"""
        
        # Add the debug endpoint
        if "@router.post(\"/debug-formdata\"" not in updated_content:
            updated_content += debug_endpoint
        
        # Write the updated content back to the file
        with open(companies_file, 'w') as file:
            file.write(updated_content)
        
        print(f"Successfully patched {companies_file} with FormData array fixes")
        return True
    
    except Exception as e:
        print(f"Error patching companies.py: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def create_test_script():
    """
    Creates a test script to verify the FormData array fixes
    """
    test_script = "test_formdata_fix.py"
    
    test_content = '''#!/usr/bin/env python3

"""
Test script to verify FormData array handling in the API
"""

import requests
import json
import logging
import os
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API configuration
API_BASE_URL = "http://127.0.0.1:8088/api/v1"
COMPANY_ID = "test_company"

def get_test_token() -> str:
    """Get a development token for testing"""
    auth_data = {
        "username": "test@example.com",
        "password": "password"
    }
    
    try:
        auth_response = requests.post(
            f"{API_BASE_URL}/auth/token",
            data=auth_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if auth_response.status_code == 200:
            token_data = auth_response.json()
            return token_data.get("access_token")
        else:
            logger.error(f"Authentication failed: {auth_response.status_code}")
            logger.error(f"Response: {auth_response.text}")
            return "DEVELOPMENT_MOCK_TOKEN_FOR_TESTING"
    except Exception as e:
        logger.error(f"Error getting token: {str(e)}")
        return "DEVELOPMENT_MOCK_TOKEN_FOR_TESTING"

def get_active_company(token: str) -> Dict[str, Any]:
    """Get the active company details"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/companies/active",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Get company failed: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return {}
    except Exception as e:
        logger.error(f"Error getting company: {str(e)}")
        return {}

def test_debug_endpoint(token: str) -> bool:
    """Test the debug FormData endpoint"""
    logger.info("Testing FormData debug endpoint...")
    
    # Test with various FormData array formats
    files = {}
    
    # Method 1: Array with indexed notation
    data1 = {
        "name": "FormData Test (indexed notation)",
        "description": "Testing with indexed array notation",
        "brand_colors[0]": "#FF5733",
        "brand_colors[1]": "#33FF57",
        "brand_colors[2]": "#3357FF"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/companies/debug-formdata",
            headers={"Authorization": f"Bearer {token}"},
            data=data1,
            files=files
        )
        
        logger.info(f"Debug endpoint response (indexed): {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Parsed arrays: {result.get('parsed_arrays')}")
            logger.info(f"Raw keys: {result.get('raw_keys')}")
            
            # Verify the array was parsed correctly
            parsed_brand_colors = result.get('parsed_arrays', {}).get('brand_colors')
            if parsed_brand_colors and len(parsed_brand_colors) == 3:
                logger.info("✓ Indexed array notation parsed correctly")
            else:
                logger.error("✗ Indexed array notation not parsed correctly")
                return False
        else:
            logger.error(f"Debug endpoint failed: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error testing debug endpoint: {str(e)}")
        return False
    
    # Method 2: JSON stringified array
    data2 = {
        "name": "FormData Test (JSON string)",
        "description": "Testing with JSON stringified array",
        "brand_colors": json.dumps(["#FF5733", "#33FF57", "#3357FF"])
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/companies/debug-formdata",
            headers={"Authorization": f"Bearer {token}"},
            data=data2,
            files=files
        )
        
        logger.info(f"Debug endpoint response (JSON string): {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Parsed arrays: {result.get('parsed_arrays')}")
            logger.info(f"Raw keys: {result.get('raw_keys')}")
            
            # Verify the array was parsed correctly
            parsed_brand_colors = result.get('parsed_arrays', {}).get('brand_colors')
            if parsed_brand_colors and len(parsed_brand_colors) == 3:
                logger.info("✓ JSON stringified array parsed correctly")
            else:
                logger.error("✗ JSON stringified array not parsed correctly")
                return False
        else:
            logger.error(f"Debug endpoint failed: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error testing debug endpoint: {str(e)}")
        return False
    
    return True

def test_company_update(token: str) -> bool:
    """Test updating company with brand colors"""
    logger.info("Testing company update with brand colors...")
    
    # Get current company first
    company = get_active_company(token)
    if not company:
        logger.error("Couldn't get active company")
        return False
    
    company_id = company.get("id", COMPANY_ID)
    logger.info(f"Current company: {company.get('name')}")
    logger.info(f"Current colors: {company.get('brand_colors', [])}")
    
    # Update with new brand colors using indexed notation
    new_colors = ["#AA1122", "#22AA11", "#1122AA"]
    
    # Method 1: Using indexed notation
    data = {
        "name": "Updated Colors (indexed)",
        "description": company.get("description", ""),
        "email": company.get("email", "test@example.com"),
        "phone": company.get("phone", ""),
        "address": company.get("address", ""),
        "logo_url": company.get("logo_url", "")
    }
    
    # Add colors with indexed notation
    for i, color in enumerate(new_colors):
        data[f"brand_colors[{i}]"] = color
    
    try:
        response = requests.put(
            f"{API_BASE_URL}/companies/{company_id}",
            headers={"Authorization": f"Bearer {token}"},
            data=data
        )
        
        logger.info(f"Update response (indexed): {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Updated company: {result.get('name')}")
            logger.info(f"Updated colors: {result.get('brand_colors', [])}")
            
            # Verify colors were updated
            updated_colors = result.get('brand_colors', [])
            if set(updated_colors) == set(new_colors):
                logger.info("✓ Colors updated correctly (indexed notation)")
            else:
                logger.error(f"✗ Colors not updated correctly. Expected {new_colors}, got {updated_colors}")
                return False
                
            # Check persistence
            get_response = requests.get(
                f"{API_BASE_URL}/companies/active",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if get_response.status_code == 200:
                check_company = get_response.json()
                check_colors = check_company.get('brand_colors', [])
                
                if set(check_colors) == set(new_colors):
                    logger.info("✓ Colors persist after retrieval")
                else:
                    logger.error(f"✗ Colors don't persist. Expected {new_colors}, got {check_colors}")
                    return False
            else:
                logger.error(f"Failed to verify colors: {get_response.status_code}")
                return False
        else:
            logger.error(f"Update failed: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error updating company: {str(e)}")
        return False
    
    # Method 2: Using JSON stringified array
    new_colors = ["#BB3344", "#44BB33", "#3344BB"]
    
    data = {
        "name": "Updated Colors (JSON)",
        "description": company.get("description", ""),
        "email": company.get("email", "test@example.com"),
        "phone": company.get("phone", ""),
        "address": company.get("address", ""),
        "logo_url": company.get("logo_url", ""),
        "brand_colors": json.dumps(new_colors)
    }
    
    try:
        response = requests.put(
            f"{API_BASE_URL}/companies/{company_id}",
            headers={"Authorization": f"Bearer {token}"},
            data=data
        )
        
        logger.info(f"Update response (JSON): {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Updated company: {result.get('name')}")
            logger.info(f"Updated colors: {result.get('brand_colors', [])}")
            
            # Verify colors were updated
            updated_colors = result.get('brand_colors', [])
            if set(updated_colors) == set(new_colors):
                logger.info("✓ Colors updated correctly (JSON notation)")
            else:
                logger.error(f"✗ Colors not updated correctly. Expected {new_colors}, got {updated_colors}")
                return False
                
            # Check persistence
            get_response = requests.get(
                f"{API_BASE_URL}/companies/active",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if get_response.status_code == 200:
                check_company = get_response.json()
                check_colors = check_company.get('brand_colors', [])
                
                if set(check_colors) == set(new_colors):
                    logger.info("✓ Colors persist after retrieval")
                else:
                    logger.error(f"✗ Colors don't persist. Expected {new_colors}, got {check_colors}")
                    return False
            else:
                logger.error(f"Failed to verify colors: {get_response.status_code}")
                return False
        else:
            logger.error(f"Update failed: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error updating company: {str(e)}")
        return False
    
    return True

def main():
    """Main test function"""
    logger.info("Starting FormData array handling test...")
    
    # Get test token
    token = get_test_token()
    if not token:
        logger.error("Failed to get authentication token")
        return False
    
    # Run tests
    debug_ok = test_debug_endpoint(token)
    update_ok = test_company_update(token)
    
    # Report results
    all_passed = debug_ok and update_ok
    
    if all_passed:
        logger.info("\n✅ All FormData tests passed!")
    else:
        logger.error("\n❌ Some FormData tests failed!")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
'''
    
    try:
        with open(test_script, 'w') as file:
            file.write(test_content)
        
        os.chmod(test_script, 0o755)  # Make it executable
        print(f"Created test script: {test_script}")
        return True
    except Exception as e:
        print(f"Error creating test script: {str(e)}")
        return False

def main():
    """Main function to apply all fixes"""
    print("Applying fixes for FormData array handling...")
    
    # Apply patches
    companies_patched = patch_companies_file()
    test_script_created = create_test_script()
    
    if companies_patched and test_script_created:
        print("\nAll fixes have been applied successfully!")
        print("\nTo test the fix:")
        print("1. Restart the API server")
        print("2. Run ./test_formdata_fix.py")
        print("3. Try the FormData tests in the debug UI")
        return 0
    else:
        print("\nSome fixes failed to apply. See errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
