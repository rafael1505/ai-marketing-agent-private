#!/usr/bin/env python3

"""
Quick fix script to correct the Dict import error in companies.py
"""

import os
import sys
import re
import fileinput

def fix_companies_file():
    """Fix the Dict type annotation issue in companies.py"""
    companies_file = os.path.join('app', 'api', 'v1', 'companies.py')
    
    try:
        # First, ensure typing import includes Dict
        with open(companies_file, 'r') as file:
            content = file.read()
        
        # Check if Dict is already imported from typing
        if "from typing import" in content and "Dict" not in content.split("from typing import")[1].split("\n")[0]:
            # Add Dict to the imports
            content = re.sub(
                r"from typing import (.*?)\n", 
                r"from typing import \1, Dict\n", 
                content
            )
        
        # Fix the response_model
        content = content.replace(
            '@router.post("/debug-formdata", response_model=Dict[str, Any])',
            '@router.post("/debug-formdata", response_model=dict)'
        )
        
        # Write back the changes
        with open(companies_file, 'w') as file:
            file.write(content)
        
        print(f"Fixed Dict import and response_model in {companies_file}")
        return True
    
    except Exception as e:
        print(f"Error fixing companies.py: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if fix_companies_file():
        print("Fix applied successfully!")
    else:
        print("Failed to apply fix.")
        sys.exit(1)
