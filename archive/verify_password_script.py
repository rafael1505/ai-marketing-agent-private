from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# Values to test
plain_password_to_test = "testpassword"
hashed_password_from_db = "$2b$12$fU.pLtASUmYYgQB9QdO69e0Vv8V0.q4h4i7fk/p6u24H.RDja9u1a" # This is the one from app/main.py

is_match = verify_password(plain_password_to_test, hashed_password_from_db)
correct_hash_for_testpassword = get_password_hash(plain_password_to_test)

output = f"""Password match for ('{plain_password_to_test}', '{hashed_password_from_db}'): {is_match}
Correct hash for '{plain_password_to_test}': {correct_hash_for_testpassword}
"""

with open("verification_result.txt", "w") as f:
    f.write(output)

print(output)
