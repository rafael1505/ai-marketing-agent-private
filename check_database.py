import asyncio
import logging
from app.db.mock_db import AsyncIOMotorClientMock
from app.core.auth import verify_password
from app.core.config import settings
import json

logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def check_database():
    print("============= DATABASE STRUCTURE CHECK =============")
    # Initialize the mock database client
    client = AsyncIOMotorClientMock()
    db = client["mock_db"]
    
    # Check if collections exist
    print("\n1. CHECKING COLLECTIONS:")
    collections = ["users", "companies", "materials"]
    for collection_name in collections:
        try:
            collection = getattr(db, collection_name)
            print(f"Collection '{collection_name}' exists: {collection is not None}")
        except AttributeError:
            print(f"Collection '{collection_name}' does not exist!")
    
    # Try to find the test user
    print("\n2. CHECKING TEST USER:")
    try:
        users_collection = db.users
        
        # Direct email query
        user = await users_collection.find_one({"email": "test@example.com"})
        print(f"Test user found by email: {user is not None}")
        
        if user:
            print(f"User data: {json.dumps(user, default=str, indent=2)}")
            
            # Test password verification
            print("\n3. TESTING PASSWORD VERIFICATION:")
            result = verify_password("password", user.get("hashed_password", ""))
            print(f"Password verification result: {result}")
            
            # Check active flags
            print("\n4. CHECKING USER STATUS:")
            print(f"'active' flag: {user.get('active')}")
            print(f"'is_active' flag: {user.get('is_active')}")
        else:
            # Try a more generic query to see if there are any users at all
            all_users = await users_collection.find().to_list(100)
            print(f"Total users in database: {len(all_users)}")
            if all_users:
                print("First user found:")
                print(json.dumps(all_users[0], default=str, indent=2))
                
    except Exception as e:
        print(f"Error checking user: {str(e)}")
        import traceback
        traceback.print_exc()

    # Test inserting and retrieving a new user
    print("\n5. TESTING USER INSERTION AND RETRIEVAL:")
    try:
        from app.core.auth import get_password_hash
        from datetime import datetime
        from bson.objectid import ObjectId
        
        test_user_id = ObjectId()
        test_user = {
            "_id": test_user_id,
            "name": "Test Insert User",
            "email": "testinsert@example.com",
            "hashed_password": get_password_hash("testpassword"),
            "active": True,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await db.users.insert_one(test_user)
        print("Test user inserted")
        
        # Retrieve the test user
        inserted_user = await db.users.find_one({"email": "testinsert@example.com"})
        print(f"Inserted user found: {inserted_user is not None}")
        if inserted_user:
            print(f"Retrieved user: {json.dumps(inserted_user, default=str, indent=2)}")
            # Check password verification
            result = verify_password("testpassword", inserted_user.get("hashed_password", ""))
            print(f"Password verification for inserted user: {result}")
    except Exception as e:
        print(f"Error in test insertion: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_database())
