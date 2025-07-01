#!/usr/bin/env python3
import asyncio
import bcrypt
from bson.objectid import ObjectId
from datetime import datetime
import json
import logging
import sys

logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                   stream=sys.stdout)

class SimpleMockDB:
    def __init__(self):
        self.users = []  # Simple in-memory list to store users
    
    async def find_one(self, query):
        logging.debug(f"Searching with query: {query}")
        if "email" in query:
            email = query["email"]
            for user in self.users:
                if user.get("email") == email:
                    logging.debug(f"Found user: {user}")
                    return user
        return None
    
    async def insert_one(self, document):
        self.users.append(document)
        logging.debug(f"Inserted user: {document}")
        return None

def verify_password(plain_password, hashed_password):
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'), 
            hashed_password.encode('utf-8')
        )
    except Exception as e:
        logging.error(f"Error verifying password: {e}")
        return False

def get_password_hash(password):
    return bcrypt.hashpw(
        password.encode('utf-8'), 
        bcrypt.gensalt(12)
    ).decode('utf-8')

async def test_user_login():
    print("\n=== SIMPLIFIED AUTH TEST ===\n")
    
    # Create mock DB
    db = SimpleMockDB()
    
    # The stored password hash from main.py
    stored_hash = "$2b$12$fU.pLtASUmYYgQB9QdO69e0Vv8V0.q4h4i7fk/p6u24H.RDja9u1a"
    
    # 1. Create and insert test user
    print("1. Creating test user with stored hash")
    test_user = {
        "_id": ObjectId(),
        "name": "Test User",
        "email": "test@example.com",
        "hashed_password": stored_hash,
        "active": True,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    await db.insert_one(test_user)
    
    # 2. Try to authenticate with correct password
    print("\n2. Testing authentication with correct password")
    user = await db.find_one({"email": "test@example.com"})
    if user:
        result = verify_password("password", user.get("hashed_password", ""))
        print(f"Authentication result: {result}")
    else:
        print("User not found!")
    
    # 3. Create a fresh user with a new hash
    print("\n3. Creating fresh user with new hash")
    fresh_hash = get_password_hash("testpass")
    fresh_user = {
        "_id": ObjectId(),
        "name": "Fresh User",
        "email": "fresh@example.com",
        "hashed_password": fresh_hash,
        "active": True,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    await db.insert_one(fresh_user)
    
    # 4. Try to authenticate with the fresh user
    print("\n4. Testing authentication with fresh user")
    fresh = await db.find_one({"email": "fresh@example.com"})
    if fresh:
        result = verify_password("testpass", fresh.get("hashed_password", ""))
        print(f"Authentication result for fresh user: {result}")
    else:
        print("Fresh user not found!")
    
    # 5. Direct hash verification
    print("\n5. Direct hash verification check")
    direct_result = verify_password("password", stored_hash)
    print(f"Direct verification result: {direct_result}")

if __name__ == "__main__":
    asyncio.run(test_user_login())
