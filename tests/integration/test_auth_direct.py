#!/usr/bin/env python3
import asyncio
import logging
import sys
from app.core.auth import verify_password, get_password_hash
from app.db.mock_db import AsyncIOMotorClientMock
from app.db.user import UserDB
from bson.objectid import ObjectId
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("auth_debug")

async def debug_auth_flow():
    """
    Test the complete authentication flow without using the API
    """
    logger.info("=== AUTHENTICATION FLOW DEBUG ===")
    
    # Initialize mock database
    mongo_client = AsyncIOMotorClientMock()
    db = mongo_client["mock_db"]
    collection = db.users
    
    # Hard-coded values from app/main.py init_test_data()
    test_email = "test@example.com"
    test_password = "password"
    stored_hash = "$2b$12$fU.pLtASUmYYgQB9QdO69e0Vv8V0.q4h4i7fk/p6u24H.RDja9u1a"
    
    # Create test user directly
    logger.info("1. Creating test user in mock DB")
    test_user = {
        "_id": ObjectId(),
        "name": "Test User",
        "full_name": "Test User",
        "email": test_email,
        "hashed_password": stored_hash,
        "active": True,
        "is_admin": True,
        "company_id": "test_company",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    await collection.insert_one(test_user)
    
    # Verify the user was created
    logger.info("2. Verifying user exists in mock DB")
    user = await collection.find_one({"email": test_email})
    if user:
        logger.info(f"User found: {user}")
    else:
        logger.error("User not found in database!")
        return
    
    # Test direct password verification
    logger.info("3. Testing direct password verification")
    hash_from_db = user.get("hashed_password", "")
    result = verify_password(test_password, hash_from_db)
    logger.info(f"Direct password verification result: {result}")
    
    # Try direct bcrypt verification
    logger.info("4. Testing with bcrypt directly")
    import bcrypt
    try:
        bcrypt_result = bcrypt.checkpw(
            test_password.encode(), 
            hash_from_db.encode()
        )
        logger.info(f"Direct bcrypt verification result: {bcrypt_result}")
    except Exception as e:
        logger.error(f"Bcrypt verification failed: {e}")
    
    # Use UserDB authenticate method
    logger.info("5. Testing UserDB.authenticate")
    user_db = UserDB(collection)
    
    auth_result = await user_db.authenticate(test_email, test_password)
    if auth_result:
        logger.info(f"Authentication successful: {auth_result}")
    else:
        logger.error("Authentication failed!")
        
    # Create new user with fresh hash
    logger.info("\n6. Testing with a fresh password hash")
    fresh_hash = get_password_hash(test_password)
    logger.info(f"Fresh hash for '{test_password}': {fresh_hash}")
    
    fresh_user = {
        "_id": ObjectId(),
        "name": "Fresh User",
        "full_name": "Fresh User",
        "email": "fresh@example.com",
        "hashed_password": fresh_hash,
        "active": True,
        "is_admin": False,
        "company_id": "test_company",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    await collection.insert_one(fresh_user)
    
    # Test authenticating with fresh user
    fresh_auth = await user_db.authenticate("fresh@example.com", test_password)
    if fresh_auth:
        logger.info(f"Fresh user authentication successful: {fresh_auth}")
    else:
        logger.error("Fresh user authentication failed!")

if __name__ == "__main__":
    asyncio.run(debug_auth_flow())
