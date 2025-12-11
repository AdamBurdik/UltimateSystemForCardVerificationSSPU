"""
Tests for authentication utilities (JWT, password hashing)
"""
import pytest
from datetime import timedelta
from fastapi import HTTPException

from src.auth_utils import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token
)


class TestPasswordHashing:
    """Test password hashing and verification"""
    
    def test_password_hash_and_verify(self):
        """Test password hashing and verification"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        # Hash should be different from original
        assert hashed != password
        
        # Should verify correctly
        assert verify_password(password, hashed) is True
    
    def test_password_verify_wrong_password(self):
        """Test verification with wrong password"""
        password = "correctpassword"
        hashed = get_password_hash(password)
        
        assert verify_password("wrongpassword", hashed) is False
    
    def test_password_hash_different_each_time(self):
        """Test that same password produces different hashes (salt)"""
        password = "testpassword"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # Hashes should be different due to salt
        assert hash1 != hash2
        
        # But both should verify the password
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestJWTTokens:
    """Test JWT token creation and decoding"""
    
    def test_create_access_token(self):
        """Test creating JWT access token"""
        data = {"sub": "123", "username": "testuser"}
        token = create_access_token(data)
        
        # Token should be a non-empty string
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Should start with JWT header
        assert token.count(".") == 2  # JWT has 3 parts separated by dots
    
    def test_decode_access_token(self):
        """Test decoding JWT access token"""
        data = {"sub": "123", "username": "testuser"}
        token = create_access_token(data)
        
        decoded = decode_access_token(token)
        
        assert decoded["sub"] == "123"
        assert decoded["username"] == "testuser"
        assert "exp" in decoded  # Expiration should be added
    
    def test_decode_invalid_token(self):
        """Test decoding invalid token raises exception"""
        with pytest.raises(HTTPException) as exc_info:
            decode_access_token("invalid-token-string")
        
        assert exc_info.value.status_code == 401
    
    def test_decode_expired_token(self):
        """Test decoding expired token"""
        # Create token that expires immediately
        data = {"sub": "123"}
        token = create_access_token(data, expires_delta=timedelta(seconds=-1))
        
        # Decoding should raise exception
        with pytest.raises(HTTPException) as exc_info:
            decode_access_token(token)
        
        assert exc_info.value.status_code == 401
    
    def test_token_with_custom_expiration(self):
        """Test creating token with custom expiration"""
        data = {"sub": "123"}
        token = create_access_token(data, expires_delta=timedelta(hours=1))
        
        decoded = decode_access_token(token)
        
        # Should have expiration claim
        assert "exp" in decoded
        
        # Should decode successfully (not expired)
        assert decoded["sub"] == "123"


class TestTokenDataStructure:
    """Test token data structure and claims"""
    
    def test_token_includes_all_claims(self):
        """Test that token includes all provided claims"""
        data = {
            "sub": "123",
            "username": "testuser",
            "email": "test@example.com",
            "custom_claim": "custom_value"
        }
        
        token = create_access_token(data)
        decoded = decode_access_token(token)
        
        # All original claims should be present
        assert decoded["sub"] == "123"
        assert decoded["username"] == "testuser"
        assert decoded["email"] == "test@example.com"
        assert decoded["custom_claim"] == "custom_value"
    
    def test_token_expiration_claim(self):
        """Test that expiration claim is added"""
        from datetime import datetime
        
        data = {"sub": "123"}
        token = create_access_token(data)
        decoded = decode_access_token(token)
        
        # Should have exp claim
        assert "exp" in decoded
        
        # Expiration should be in the future
        exp_timestamp = decoded["exp"]
        assert exp_timestamp > datetime.utcnow().timestamp()
