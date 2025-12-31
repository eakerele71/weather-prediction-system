"""Manual test for authentication"""
from app.auth import (
    verify_password,
    get_password_hash,
    authenticate_user,
    create_access_token,
    get_user
)

print("Testing authentication module...")
print()

# Test 1: Password hashing
print("Test 1: Password hashing")
password = "testpassword"
hashed = get_password_hash(password)
print(f"  Password: {password}")
print(f"  Hashed: {hashed[:20]}...")
print(f"  Verification: {verify_password(password, hashed)}")
print()

# Test 2: Get user
print("Test 2: Get user")
user = get_user("testuser")
print(f"  Username: {user.username if user else 'None'}")
print(f"  Email: {user.email if user else 'None'}")
print()

# Test 3: Authenticate valid user
print("Test 3: Authenticate valid user")
user = authenticate_user("testuser", "secret")
print(f"  Result: {'Success' if user else 'Failed'}")
print(f"  Username: {user.username if user else 'None'}")
print()

# Test 4: Authenticate with wrong password
print("Test 4: Authenticate with wrong password")
user = authenticate_user("testuser", "wrongpassword")
print(f"  Result: {'Success (UNEXPECTED!)' if user else 'Failed (expected)'}")
print()

# Test 5: Create token
print("Test 5: Create token")
token = create_access_token({"sub": "testuser"})
print(f"  Token created: {token[:50]}...")
print()

print("All manual tests completed!")
