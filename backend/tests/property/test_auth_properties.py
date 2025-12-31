"""Property-based tests for authentication"""
import pytest
from hypothesis import given, strategies as st
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from app.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user,
    authenticate_user
)


# Feature: weather-prediction-system, Property 15: API Authentication
@given(st.text(min_size=1, max_size=100))
def test_password_roundtrip(password):
    """
    Property 15: API Authentication
    For any password, hashing and then verifying should succeed
    """
    hashed = get_password_hash(password)
    assert verify_password(password, hashed)


# Feature: weather-prediction-system, Property 15: API Authentication
@given(
    password=st.text(min_size=1, max_size=100),
    wrong_password=st.text(min_size=1, max_size=100)
)
def test_wrong_password_fails(password, wrong_password):
    """
    Property 15: API Authentication
    For any password and different wrong password, verification should fail
    """
    if password == wrong_password:
        return  # Skip if passwords are the same
    
    hashed = get_password_hash(password)
    assert not verify_password(wrong_password, hashed)


# Feature: weather-prediction-system, Property 15: API Authentication
@given(st.text(min_size=1, max_size=50, alphabet=st.characters(min_codepoint=97, max_codepoint=122)))
def test_token_creation_always_succeeds(username):
    """
    Property 15: API Authentication
    For any valid username, token creation should succeed
    """
    token = create_access_token({"sub": username})
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0


# Feature: weather-prediction-system, Property 15: API Authentication
@given(st.text(min_size=1, max_size=100))
@pytest.mark.asyncio
async def test_invalid_token_always_rejected(invalid_token):
    """
    Property 15: API Authentication
    For any invalid token string, authentication should fail with 401
    """
    # Skip if by chance we generate a valid JWT structure
    if invalid_token.count('.') == 2:
        return
    
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=invalid_token)
    
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(credentials)
    
    assert exc_info.value.status_code == 401


# Feature: weather-prediction-system, Property 15: API Authentication
def test_valid_user_authentication():
    """
    Property 15: API Authentication
    Valid credentials should always authenticate successfully
    """
    user = authenticate_user("testuser", "secret")
    assert user is not None
    assert user.username == "testuser"


# Feature: weather-prediction-system, Property 15: API Authentication
@given(st.text(min_size=1, max_size=50))
def test_invalid_username_authentication_fails(username):
    """
    Property 15: API Authentication
    For any username that doesn't exist, authentication should fail
    """
    # Skip the test user
    if username == "testuser":
        return
    
    user = authenticate_user(username, "anypassword")
    assert user is None


# Feature: weather-prediction-system, Property 15: API Authentication
@given(st.text(min_size=1, max_size=100))
def test_wrong_password_authentication_fails(wrong_password):
    """
    Property 15: API Authentication
    For any wrong password, authentication should fail
    """
    # Skip the correct password
    if wrong_password == "secret":
        return
    
    user = authenticate_user("testuser", wrong_password)
    assert user is None


# Feature: weather-prediction-system, Property 15: API Authentication
@given(st.text(min_size=1, max_size=50, alphabet=st.characters(min_codepoint=97, max_codepoint=122)))
@pytest.mark.asyncio
async def test_valid_token_for_existing_user(username):
    """
    Property 15: API Authentication
    For the existing test user, a valid token should authenticate successfully
    """
    # Only test with the existing user
    if username != "testuser":
        username = "testuser"
    
    token = create_access_token({"sub": username})
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    
    user = await get_current_user(credentials)
    assert user is not None
    assert user.username == username


# Feature: weather-prediction-system, Property 15: API Authentication
@given(st.text(min_size=1, max_size=50))
@pytest.mark.asyncio
async def test_token_for_nonexistent_user_fails(username):
    """
    Property 15: API Authentication
    For any non-existent user, even with valid token structure, authentication should fail
    """
    # Skip the existing test user
    if username == "testuser":
        return
    
    token = create_access_token({"sub": username})
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(credentials)
    
    assert exc_info.value.status_code == 401


# Feature: weather-prediction-system, Property 15: API Authentication
@given(st.text(min_size=1, max_size=100))
def test_password_hash_uniqueness(password):
    """
    Property 15: API Authentication
    For any password, multiple hashes should be different (salt randomness)
    """
    hash1 = get_password_hash(password)
    hash2 = get_password_hash(password)
    
    # Hashes should be different due to salt
    assert hash1 != hash2
    # But both should verify correctly
    assert verify_password(password, hash1)
    assert verify_password(password, hash2)
