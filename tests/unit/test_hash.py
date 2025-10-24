from app.core.auth import verify_password, get_password_hash

def test_hash_verify():
    # Test normal password hashing and verification
    password = "password"
    hashed = get_password_hash(password)
    
    print(f"Original password: {password}")
    print(f"Hashed password: {hashed}")
    
    # Test verification
    is_correct = verify_password(password, hashed)
    print(f"Verification with correct password: {is_correct}")
    
    # Test with incorrect password
    is_incorrect = verify_password("wrongpassword", hashed)
    print(f"Verification with incorrect password: {is_incorrect}")
    
    # Test verification with known hash
    test_hash = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"  # Hash for "password"
    is_valid = verify_password("password", test_hash)
    print(f"Verification with known hash: {is_valid}")

if __name__ == "__main__":
    test_hash_verify()
