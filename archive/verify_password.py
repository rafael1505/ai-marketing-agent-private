from passlib.context import CryptContext
import sys
import passlib

# Print passlib version
print(f"Passlib version: {passlib.__version__}")

# Define the same password context as in our application
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    print(f"Verifying password: '{plain_password}' against hash: '{hashed_password}'")
    result = pwd_context.verify(plain_password, hashed_password)
    print(f"Verification result: {result}")
    return result

def get_password_hash(password):
    print(f"Hashing password: '{password}'")
    result = pwd_context.hash(password)
    print(f"Resulting hash: '{result}'")
    return result

if __name__ == "__main__":
    # Test with the hash value we're using in our application
    known_hash = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"
    password = "password"
    
    print("\nTest 1: Verify known hash")
    verify_password(password, known_hash)
    
    print("\nTest 2: Generate new hash and verify")
    new_hash = get_password_hash(password)
    verify_password(password, new_hash)
    
    # If a command line parameter is provided, use it as the password
    if len(sys.argv) > 1:
        test_password = sys.argv[1]
        print(f"\nTest 3: Using provided password: '{test_password}'")
        verify_password(test_password, known_hash)
