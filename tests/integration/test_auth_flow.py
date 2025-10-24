import asyncio
import logging
from app.db.mock_db import AsyncIOMotorClientMock
from app.db.user import UserDB
from app.core.auth import verify_password, get_password_hash

logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def test_user_auth():
    print("\n=== TESTING USER AUTHENTICATION FLOW ===")
    
    # Initialize mock DB
    client = AsyncIOMotorClientMock()
    db = client["mock_db"]
    user_db = UserDB(db.users)
    
    # Test data - this is what's stored in main.py
    test_email = "test@example.com"
    test_password = "password"
    stored_hash = "$2b$12$fU.pLtASUmYYgQB9QdO69e0Vv8V0.q4h4i7fk/p6u24H.RDja9u1a"
    
    # 1. Check if user exists in DB
    print("\n1. Checking if test user exists:")
    user = await user_db.get_by_email(test_email)
    if user:
        print(f"Found user: {user}")
        
        # 2. Test direct password verification
        print("\n2. Testing direct password verification:")
        hashed_pw = user.get("hashed_password", "")
        result = verify_password(test_password, hashed_pw)
        print(f"Direct verify_password result: {result}")
        
        # 3. Compare stored hash with what's in the DB
        print("\n3. Comparing hashes:")
        print(f"Hash in DB:   {hashed_pw}")
        print(f"Expected hash: {stored_hash}")
        print(f"Hashes match: {hashed_pw == stored_hash}")
    else:
        print(f"Test user not found in database!")
        
    # 4. Test the authenticate method directly
    print("\n4. Testing authenticate method:")
    auth_result = await user_db.authenticate(test_email, test_password)
    print(f"Authentication result: {auth_result is not None}")
    
    # 5. Create and authenticate with a new test user
    print("\n5. Creating new test user:")
    try:
        from app.models.user import UserCreate
        from datetime import datetime
        
        # Create a new test user
        new_user_data = {
            "name": "New Test User",
            "email": "newtest@example.com",
            "password": "password123",
            "is_admin": False,
            "company_id": "test_company"
        }
        
        # Using UserDB's create_user method
        from app.core.config import settings
        from app.models.user import UserCreate
        
        user_create = UserCreate(**new_user_data)
        new_user = await user_db.create_user(user_create)
        print(f"New user created: {new_user}")
        
        # Test authenticating with the new user
        print("\n6. Authenticating with new user:")
        auth_result = await user_db.authenticate(new_user_data["email"], new_user_data["password"])
        print(f"Authentication result for new user: {auth_result is not None}")
        
    except Exception as e:
        print(f"Error creating/authenticating new test user: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_user_auth())
