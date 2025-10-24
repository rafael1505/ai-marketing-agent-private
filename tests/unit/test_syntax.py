#!/usr/bin/env python3

"""
Simplified version of the companies.py file to isolate syntax issues
"""

import sys
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    print("Starting test...")
    
    # Simulate the problematic code section
    logger.info("Processing FormData request")
    try:
        print("Inside try block")
        logger.info("Form data keys: []")
        
        # Import the module (this is where the error was occurring)
        print("Importing module...")
        from app.core.formdata_array_fix import get_parsed_form_arrays, parse_formdata_arrays
        print("Module imported successfully!")
        
    except ImportError as e:
        print(f"Import error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        
    print("Test completed!")

if __name__ == "__main__":
    # Add project root to path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    main()
