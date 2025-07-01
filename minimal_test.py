#!/usr/bin/env python3
import bcrypt

def main():
    # The hardcoded hash from main.py for test@example.com
    stored_hash = "$2b$12$fU.pLtASUmYYgQB9QdO69e0Vv8V0.q4h4i7fk/p6u24H.RDja9u1a"
    password = "password"
    
    # Test password verification
    print("Testing if password matches stored hash")
    result = bcrypt.checkpw(password.encode(), stored_hash.encode())
    print(f"Result: {result}")
    
    # Create a new hash
    print("Creating new hash")
    new_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    print(f"New hash: {new_hash}")
    print(f"Verification with new hash: {bcrypt.checkpw(password.encode(), new_hash.encode())}")

if __name__ == "__main__":
    main()
