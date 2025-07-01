import asyncio
import logging
import sys
from fastapi import FastAPI
from app.db.mock_db import AsyncIOMotorClientMock, MockDatabase
from app.core.auth import verify_password, get_password_hash
from app.db.user import UserDB
from bson.objectid import ObjectId
from datetime import datetime

# Configure logging to console
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                   stream=sys.stdout)
logger = logging.getLogger(__name__)

async def debug_database():
    logger.info("Starting database debugging")
    
    # Initialize database
    client = AsyncIOMotorClientMock()
    db = client["test_db"]
    
    # Create a test user with a fresh hash
    hashed_pwd = get_password_hash("password")
    logger.info(f"Generated hash for test user: {hashed_pwd}")
    
    test_user = {
        "_id": ObjectId(),
        "name": "Test User",
        "full_name": "Test User", 
        "email": "test@example.com",
        "hashed_password": hashed_pwd,
        "active": True,
        "is_admin": True,
        "company_id": "test_company",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Insert user
    try:
        await db.users.insert_one(test_user)
        logger.info("Test user inserted successfully")
    except Exception as e:
        logger.error(f"Error inserting test user: {e}")
        return
    
    # Try to retrieve the user by email
    try:
        user_db = UserDB(db.users)
        fetched_user = await user_db.get_by_email("test@example.com")
        if fetched_user:
            logger.info(f"User retrieved successfully: {fetched_user}")
        else:
            logger.error("Failed to retrieve user by email")
    except Exception as e:
        logger.error(f"Error retrieving user by email: {e}")
    
    # Test authentication
    try:
        auth_result = await user_db.authenticate("test@example.com", "password")
        if auth_result:
            logger.info(f"Authentication successful: {auth_result}")
        else:
            logger.error("Authentication failed")
    except Exception as e:
        logger.error(f"Error during authentication: {e}")

    # Manually test password verification
    try:
        if fetched_user:
            result = verify_password("password", fetched_user["hashed_password"])
            logger.info(f"Manual password verification: {result}")
    except Exception as e:
        logger.error(f"Error during manual password verification: {e}")

if __name__ == "__main__":
    asyncio.run(debug_database())
