devcontainers@YY321187:/mnt/c/Users/brc07274/OneDrive - Philips/Philips Files/BU
 - CI/Repository/AI Marketing Agent (Python)/ai-marketing-agent$ python3 -u "/mnt/c/Users/brc07274/OneDrive - Philips/Philips Files/BU - CI/Repository/AI Marketing Agent (Pytho
n)/ai-marketing-agent/debug_auth_server.py"
2025-05-22 13:09:12,081 - passlib.utils.compat - DEBUG - loaded lazy attr 'SafeConfigParser': <class 'configparser.ConfigParser'>
2025-05-22 13:09:12,081 - passlib.utils.compat - DEBUG - loaded lazy attr 'SafeConfigParser': <class 'configparser.ConfigParser'>
2025-05-22 13:09:12,082 - passlib.utils.compat - DEBUG - loaded lazy attr 'NativeStringIO': <class '_io.StringIO'>
2025-05-22 13:09:12,082 - passlib.utils.compat - DEBUG - loaded lazy attr 'NativeStringIO': <class '_io.StringIO'>
2025-05-22 13:09:12,082 - passlib.utils.compat - DEBUG - loaded lazy attr 'BytesIO': <class '_io.BytesIO'>
2025-05-22 13:09:12,082 - passlib.utils.compat - DEBUG - loaded lazy attr 'BytesIO': <class '_io.BytesIO'>
2025-05-22 13:09:12,183 - passlib.registry - DEBUG - registered 'bcrypt' handler: <class 'passlib.handlers.bcrypt.bcrypt'>
2025-05-22 13:09:12,183 - passlib.registry - DEBUG - registered 'bcrypt' handler: <class 'passlib.handlers.bcrypt.bcrypt'>
2025-05-22 13:09:12,467 - root - INFO - Monkey patched verify_password function for debugging
2025-05-22 13:09:12,467 - root - INFO - Monkey patched verify_password function for debugging
2025-05-22 13:09:12,468 - root - INFO - Starting debug server on 127.0.0.1:8088
2025-05-22 13:09:12,468 - root - INFO - Starting debug server on 127.0.0.1:8088
INFO:     Will watch for changes in these directories: ['/mnt/c/Users/brc07274/OneDrive - Philips/Philips Files/BU - CI/Repository/AI Marketing Agent (Python)/ai-marketing-agent']
ERROR:    [Errno 98] Address already in use
devcontainers@YY321187:/mnt/c/Users/brc07274/OneDrive - Philips/Philips Files/BU - CI/Repository/AI Marketing Agent (Python)/ai-marketing-agent$ #!/usr/bin/env python3
import bcrypt

# The hardcoded hash from main.py for test@example.com
STORED_HASH = "$2b$12$fU.pLtASUmYYgQB9QdO69e0Vv8V0.q4h4i7fk/p6u24H.RDja9u1a"
PASSWORD = "password"

def main():
    print("=== DIRECT BCRYPT VERIFICATION TEST ===")
    
    print(f"\nTesting if '{PASSWORD}' matches the stored hash")
    encoded_password = PASSWORD.encode('utf-8')
    encoded_hash = STORED_HASH.encode('utf-8')
    
    # Try verification
    print("Running bcrypt.checkpw(password, hash)...")
    try:
        result = bcrypt.checkpw(encoded_password, encoded_hash)
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")
        
    # Create a fresh hash
    print("\nCreating fresh hash for comparison:")
    try:
        salt = bcrypt.gensalt(12)  # Same rounds as the original
        new_hash = bcrypt.hashpw(encoded_password, salt)
        print(f"New hash: {new_hash.decode()}")
        
        # Verify with fresh hash
        result = bcrypt.checkpw(encoded_password, new_hash)
        print(f"Verification with fresh hash: {result}")
    except Exception as e:
        print(f"Error creating fresh hash: {e}")

if __name__ == "__main__":
    main()
