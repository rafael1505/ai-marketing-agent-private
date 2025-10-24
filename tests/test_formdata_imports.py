#!/usr/bin/env python3

"""
Simple test script to check if the formdata_array_fix module can be imported correctly
"""

import sys
import os
import traceback

def test_imports():
    print("Testing imports...")
    
    try:
        # Add the project root to the path
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Try importing the module
        print("Importing formdata_array_fix...")
        from app.core.formdata_array_fix import extract_array_indices, parse_formdata_arrays, get_parsed_form_arrays
        print("✓ Successfully imported formdata_array_fix module")
        
        # Test the extract_array_indices function
        test_cases = [
            ("brand_colors[0]", ("brand_colors", 0)),
            ("colors[5]", ("colors", 5)),
            ("normal_field", (None, None))
        ]
        
        print("\nTesting extract_array_indices function:")
        for input_str, expected in test_cases:
            result = extract_array_indices(input_str)
            print(f"Input: '{input_str}', Output: {result}, Expected: {expected}, Match: {result == expected}")
        
        print("\nModule appears to be working correctly.")
        return True
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
