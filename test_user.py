import asyncio
import logging
import sys
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from app.db.mock_db import AsyncIOMotorClientMock
from app.core.auth import verify_password, get_password_hash

# Configure logging to console
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                   stream=sys.stdout)
logger = logging.getLogger(__name__)

app = FastAPI()

async def test_authentication():
    # Create mock database client
    mongodb_client = AsyncIOMotorClientMock()
    mongodb = mongodb_client["mock_db"]
    
    # Clear existing users
    users_collection = mongodb["users"]
    
    # Create a test user
    from bson.objectid import ObjectId
    from datetime import datetime
    
    test_user = {
        "_id": ObjectId(),
        "name": "Test User",
        "full_name": "Test User",
        "email": "test@example.com",
        "hashed_password": get_password_hash("password"),
        "active": True,
        "is_admin": True,
        "company_id": "test_company",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Insert the test user
    await users_collection.insert_one(test_user)
    logger.info("Test user created")
    
    # Retrieve the user
    from app.db.user import UserDB
    user_db = UserDB(users_collection)
    user = await user_db.get_by_email("test@example.com")
    
    if user:
        logger.info(f"User found: {user['email']}")
        
        # Test authentication
        result = await user_db.authenticate("test@example.com", "password")
        if result:
            logger.info("Authentication successful")
        else:
            logger.error("Authentication failed")
    else:
        logger.error("User not found")

if __name__ == "__main__":
    try:
        print("Starting test_authentication")
        asyncio.run(test_authentication())
        print("Test completed successfully")
    except Exception as e:
        import traceback
        print(f"An error occurred: {e}")
        print(traceback.format_exc())
