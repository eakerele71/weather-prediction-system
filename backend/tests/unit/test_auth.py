"""Unit tests for authentication module"""
import pytest
from datetime import timedelta
from jose import jwt
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from app.auth import (
    verify_password,
    get_password_hash,
    authenticate_user,
    create_access_token,
    get_current_user,
    get_user,
    SECRET_KEY,
    ALGORITHM,
    User,
    UserInDB
)


class TestPasswordHashing:
    """Test password hashing and verification"""
    
    def test_password_hash_and_verify(self):
        """Test that password hashing and verification work correctly"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert verify_password(password, hashed)
    
    def test_wrong_password_fails_verification(self):
        """Test that wrong password fails verification"""
        password = "correctpassword"
        wrong_password = "wrongpassword"
        hashed = get_password_hash(password)
        
        assert not verify_password(wrong_password, hashed)
    
    def test_different_hashes_for_same_password(self):
        """Test that same password produces different hashes (salt)"""
        password = "samepassword"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        assert hash1 != hash2
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)


class TestUserRetrieval:
    """Test user retrieval from database"""
    
    def test_get_existing_user(self):
        """Test retrieving an existing user"""
        user = get_user("testuser")
        
        assert user is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert not user.disabled
    
    def test_get_nonexistent_user(self):
        """Test retrieving a non-existent user returns None"""
        user = get_user("nonexistentuser")
        
        assert user is None


class TestUserAuthentication:
    """Test user authentication"""
    
    def test_authenticate_valid_user(self):
        """Test authentication with valid credentials"""
        user = authenticate_user("testuser", "secret")
        
        assert user is not None
        assert user.username == "testuser"
    
    def test_authenticate_wrong_password(self):
        """Test authentication fails with wrong password"""
        user = authenticate_user("testuser", "wrongpassword")
        
        assert user is None
    
    def test_authenticate_nonexistent_user(self):
        """Test authentication fails for non-existent user"""
        user = authenticate_user("nonexistent", "anypassword")
        
        assert user is None


class TestTokenCreation:
    """Test JWT token creation"""
    
    def test_create_access_token(self):
        """Test creating an access token"""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        
        # Decode and verify
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "testuser"
        assert "exp" in payload
    
    def test_create_token_with_expiration(self):
        """Test creating token with custom expiration"""
        data = {"sub": "testuser"}
        expires_delta = timedelta(minutes=60)
        token = create_access_token(data, expires_delta)
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "testuser"
    
    def test_token_contains_expiration(self):
        """Test that token contains expiration claim"""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert "exp" in payload
        assert isinstance(payload["exp"], int)


class TestTokenValidation:
    """Test JWT token validation"""
    
    @pytest.mark.asyncio
    async def test_get_current_user_with_valid_token(self):
        """Test getting current user with valid token"""
        # Create valid token
        token = create_access_token({"sub": "testuser"})
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        
        # Get user
        user = await get_current_user(credentials)
        
        assert user is not None
        assert user.username == "testuser"
    
    @pytest.mark.asyncio
    async def test_get_current_user_with_invalid_token(self):
        """Test that invalid token raises exception"""
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid_token")
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials)
        
        assert exc_info.value.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_current_user_with_nonexistent_user(self):
        """Test that token for non-existent user raises exception"""
        token = create_access_token({"sub": "nonexistentuser"})
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials)
        
        assert exc_info.value.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_current_user_with_missing_subject(self):
        """Test that token without subject raises exception"""
        token = create_access_token({"other": "data"})
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials)
        
        assert exc_info.value.status_code == 401


class TestAuthenticationEdgeCases:
    """Test edge cases in authentication"""
    
    def test_empty_password(self):
        """Test authentication with empty password"""
        user = authenticate_user("testuser", "")
        
        assert user is None
    
    def test_empty_username(self):
        """Test authentication with empty username"""
        user = authenticate_user("", "secret")
        
        assert user is None
    
    def test_special_characters_in_password(self):
        """Test password with special characters"""
        password = "p@ssw0rd!#$%"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed)
