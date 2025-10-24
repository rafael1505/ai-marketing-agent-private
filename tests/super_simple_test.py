#!/usr/bin/env python3
"""
Super simple test for brand colors persistence
"""
print("Starting minimal test...")

# Basic mock database
class MockDB:
    def __init__(self):
        self.data = {}
        
    def update(self, key, value):
        self.data[key] = value
        
    def get(self, key):
        return self.data.get(key)

# Create test instance
db = MockDB()

# Initial data
colors = ["#000000"]
print(f"Initial colors: {colors}")

# Store in database
db.update("brand_colors", colors)

# Modify original list (simulating the bug)
colors.append("#FF0000")
print(f"Modified original: {colors}")

# Get from database
stored_colors = db.get("brand_colors")
print(f"From database: {stored_colors}")

# Check if modification affected stored value
if stored_colors == ["#000000"]:
    print("✅ TEST PASSED: Reference not shared")
    print("(This is incorrect behavior - our bug is somewhere else)")
else:
    print("❌ TEST FAILED: Reference shared between variables")
    print(f"Expected: ['#000000'], Got: {stored_colors}")
    
# Fixed version
print("\nTesting with fix:")
colors2 = ["#000000"]
db.update("brand_colors2", list(colors2))  # Create a new list
colors2.append("#FF0000")
stored_colors2 = db.get("brand_colors2")
print(f"Original: {colors2}, Stored: {stored_colors2}")
if stored_colors2 == ["#000000"]:
    print("✅ FIX WORKS: Reference not shared")
else:
    print("❌ FIX FAILED: Reference still shared")
    
print("\nTest complete.")
