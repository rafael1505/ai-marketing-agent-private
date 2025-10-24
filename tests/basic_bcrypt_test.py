#!/usr/bin/env python3

import bcrypt

print("=== BCRYPT PASSWORD VERIFICATION TEST ===")

# The hardcoded hash from main.py for test@example.com  
STORED_HASH = "$2b$12$fU.pLtASUmYYgQB9QdO69e0Vv8V0.q4h4i7fk/p6u24H.RDja9u1a"
PASSWORD = "password"

# Simple bcrypt check
print(f"\nTesting if '{PASSWORD}' matches the stored hash")
encoded_password = PASSWORD.encode('utf-8')
encoded_hash = STORED_HASH.encode('utf-8')

try:
    bcrypt_result = bcrypt.checkpw(encoded_password, encoded_hash)
    print(f"Verification result: {bcrypt_result}")
except Exception as e:
    print(f"Error during verification: {str(e)}")

# Create a fresh hash
print("\nCreating a new hash for comparison:")
try:
    salt = bcrypt.gensalt(12)  # Using the same rounds as the original
    new_hash = bcrypt.hashpw(encoded_password, salt)
    print(f"New hash for '{PASSWORD}': {new_hash.decode('utf-8')}")
    
    # Verify with the new hash
    verify_result = bcrypt.checkpw(encoded_password, new_hash)
    print(f"Verification with new hash: {verify_result}")
except Exception as e:
    print(f"Error creating/verifying new hash: {str(e)}")
    
# Try a different password to ensure verification can fail
print("\nTesting with incorrect password:")
wrong_password = "wrongpassword".encode('utf-8')
try:
    wrong_result = bcrypt.checkpw(wrong_password, new_hash)
    print(f"Verification with wrong password: {wrong_result}")
except Exception as e:
    print(f"Error during wrong password test: {str(e)}")

print("\n=== TEST COMPLETE ===")