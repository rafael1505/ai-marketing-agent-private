#!/usr/bin/env python3
"""
Simulates the form data array parsing logic from the companies.py endpoint
"""

# Simulate a form data request with indexed brand_colors
MOCK_FORM_DATA = {
    "name": "Test Company",
    "description": "Test Description",
    "brand_colors[0]": "#FF0000",
    "brand_colors[1]": "#00FF00",
    "brand_colors[2]": "#0000FF"
}

class MockForm:
    def __init__(self, data):
        self.data = data
        
    def __contains__(self, key):
        return key in self.data
        
    def __getitem__(self, key):
        return self.data.get(key)
        
    def keys(self):
        return self.data.keys()
        
    def getlist(self, key):
        # Simulate the getlist method for repeated form fields
        if key in self.data:
            return [self.data[key]]
        return []
        
def extract_brand_colors(form):
    """
    Extract brand_colors from form data using the logic from companies.py
    """
    print("Extracting brand_colors from form data...")
    print(f"Form keys: {list(form.keys())}")
    
    # Extract brand_colors from form data (handle both array formats)
    brand_colors = []
    
    # Method 1: Look for indexed form fields like brand_colors[0], brand_colors[1]
    color_index = 0
    while f"brand_colors[{color_index}]" in form:
        color_value = form[f"brand_colors[{color_index}]"]
        print(f"Found color at index {color_index}: {color_value}")
        if color_value and color_value.strip():
            brand_colors.append(color_value.strip())
        color_index += 1
    
    # Method 2: Look for repeated "brand_colors" fields (alternative FormData format)
    if not brand_colors and "brand_colors" in form:
        print("No indexed colors found, looking for repeated fields...")
        brand_colors_raw = form.getlist("brand_colors")
        brand_colors = [color.strip() for color in brand_colors_raw if color and color.strip()]
    
    print(f"Extracted brand_colors: {brand_colors}")
    return brand_colors

# Run the extraction test
if __name__ == "__main__":
    print("=== FORM DATA ARRAY PARSING TEST ===\n")
    
    # Create a mock form
    form = MockForm(MOCK_FORM_DATA)
    
    # Extract the brand_colors
    colors = extract_brand_colors(form)
    
    # Check if the extraction worked correctly
    expected = ["#FF0000", "#00FF00", "#0000FF"]
    success = colors == expected
    
    print(f"\nExtraction successful: {success}")
    print(f"Expected: {expected}")
    print(f"Actual: {colors}")
    
    if success:
        print("\n✅ SUCCESS: The form data array parsing logic is working correctly!")
        exit(0)
    else:
        print("\n❌ FAILED: The form data array parsing logic is not working correctly.")
        exit(1)
