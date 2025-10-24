import asyncio
import logging
import json
from app.db.mock_db import AsyncIOMotorClientMock, MockDatabase
from app.core.auth import verify_password, get_password_hash
from app.db.user import UserDB
from bson.objectid import ObjectId
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_mock_auth():
    logger.info("Starting authentication test with mock database")
    
    # Create a mock database
    client = AsyncIOMotorClientMock()
    db = client["test_db"]
    
    # Create a test user
    test_user = {
        "_id": ObjectId(),
        "name": "Test User",
        "full_name": "Test User",
        "email": "test@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password"
        "active": True,
        "is_admin": True,
        "company_id": "test_company",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    logger.info(f"Inserting test user: {test_user}")
    
    # Insert the test user
    await db.users.insert_one(test_user)
    
    # Create a UserDB instance
    user_db = UserDB(db.users)
    
    # Try to fetch the user by email
    fetched_user = await user_db.get_by_email("test@example.com")
    if fetched_user:
        logger.info(f"User fetched by email: {fetched_user}")
    else:
        logger.error("Failed to fetch user by email")
    
    # Try to authenticate
    auth_result = await user_db.authenticate("test@example.com", "password")
    if auth_result:
        logger.info("Authentication successful!")
        logger.info(f"Authenticated user: {auth_result}")
    else:
        logger.error("Authentication failed!")
        
    # Verify the password manually
    if fetched_user:
        result = verify_password("password", fetched_user["hashed_password"])
        logger.info(f"Manual password verification: {result}")

if __name__ == "__main__":
    asyncio.run(test_mock_auth())
