import asyncio
import json
import bcrypt
from passlib.context import CryptContext

# Create the same password context used in the main app
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# The hardcoded hash from main.py for test@example.com
STORED_HASH = "$2b$12$fU.pLtASUmYYgQB9QdO69e0Vv8V0.q4h4i7fk/p6u24H.RDja9u1a"

async def test_password_verification():
    print("========== PASSWORD VERIFICATION TESTS ==========")
    
    print("\n1. Testing stored hash with 'password':")
    result = verify_password("password", STORED_HASH)
    print(f"Verification result: {result}")
    
    print("\n2. Creating a new hash for 'password':")
    new_hash = get_password_hash("password")
    print(f"New hash: {new_hash}")
    
    print("\n3. Testing new hash with 'password':")
    result = verify_password("password", new_hash)
    print(f"Verification result: {result}")
    
    print("\n4. Direct bcrypt check:")
    encoded_password = "password".encode('utf-8')
    encoded_hash = STORED_HASH.encode('utf-8')
    try:
        bcrypt_result = bcrypt.checkpw(encoded_password, encoded_hash)
        print(f"Direct bcrypt verification: {bcrypt_result}")
    except Exception as e:
        print(f"Error with direct bcrypt check: {str(e)}")

    print("\n5. Creating a new hash with bcrypt:")
    try:
        salt = bcrypt.gensalt(12) 
        new_bcrypt_hash = bcrypt.hashpw(encoded_password, salt).decode('utf-8')
        print(f"New bcrypt hash: {new_bcrypt_hash}")
        print(f"Direct verification with new hash: {bcrypt.checkpw(encoded_password, new_bcrypt_hash.encode('utf-8'))}")
    except Exception as e:
        print(f"Error creating new hash: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_password_verification())
