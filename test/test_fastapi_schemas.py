"""
Tests for Pydantic schemas and validation
"""
import pytest
from pydantic import ValidationError
from src.schemas import (
    UserCreate, UserLogin, UserResponse,
    Token, CardCreate, GroupCreate, TimecardCreate
)


class TestUserSchemas:
    """Test user-related Pydantic schemas"""
    
    def test_user_create_valid(self):
        """Test creating valid user schema"""
        user = UserCreate(
            username="testuser",
            email="test@example.com",
            password="password123",
            first_name="Test",
            second_name="User"
        )
        
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.password == "password123"
    
    def test_user_create_invalid_email(self):
        """Test user creation with invalid email"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="testuser",
                email="not-an-email",
                password="password123"
            )
        
        assert "email" in str(exc_info.value).lower()
    
    def test_user_create_short_username(self):
        """Test user creation with username too short"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="ab",  # Less than 3 characters
                email="test@example.com",
                password="password123"
            )
        
        assert "username" in str(exc_info.value).lower()
    
    def test_user_create_short_password(self):
        """Test user creation with password too short"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="testuser",
                email="test@example.com",
                password="short"  # Less than 6 characters
            )
        
        assert "password" in str(exc_info.value).lower()
    
    def test_user_login_valid(self):
        """Test valid login schema"""
        login = UserLogin(
            email="test@example.com",
            password="password123"
        )
        
        assert login.email == "test@example.com"
        assert login.password == "password123"
    
    def test_user_response_from_orm(self):
        """Test user response schema with ORM data"""
        # This would typically come from a database model
        user_data = {
            "id": 1,
            "username": "testuser",
            "email": "test@example.com",
            "first_name": "Test",
            "second_name": "User",
            "is_active": True
        }
        
        user = UserResponse(**user_data)
        
        assert user.id == 1
        assert user.username == "testuser"
        assert user.is_active is True


class TestTokenSchemas:
    """Test token-related schemas"""
    
    def test_token_valid(self):
        """Test valid token schema"""
        token = Token(
            access_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            token_type="bearer"
        )
        
        assert token.access_token.startswith("eyJ")
        assert token.token_type == "bearer"
    
    def test_token_default_type(self):
        """Test token schema with default type"""
        token = Token(access_token="some-token")
        
        assert token.token_type == "bearer"


class TestCardSchemas:
    """Test card-related schemas"""
    
    def test_card_create_valid(self):
        """Test valid card creation schema"""
        card = CardCreate(
            card_number="1234567890",
            chip_number="ABCDEF1234"
        )
        
        assert card.card_number == "1234567890"
        assert card.chip_number == "ABCDEF1234"
    
    def test_card_create_invalid_card_number(self):
        """Test card with non-numeric card number"""
        with pytest.raises(ValidationError) as exc_info:
            CardCreate(
                card_number="ABC123",  # Should be only digits
                chip_number="ABCDEF"
            )
        
        assert "card_number" in str(exc_info.value).lower()
    
    def test_card_create_invalid_chip_number(self):
        """Test card with invalid chip number (not hex)"""
        with pytest.raises(ValidationError) as exc_info:
            CardCreate(
                card_number="1234567890",
                chip_number="GHIJKL"  # Should be hex characters only
            )
        
        assert "chip_number" in str(exc_info.value).lower()


class TestGroupSchemas:
    """Test group-related schemas"""
    
    def test_group_create_valid(self):
        """Test valid group creation"""
        group = GroupCreate(group_name="Teachers")
        
        assert group.group_name == "Teachers"
    
    def test_group_create_empty_name(self):
        """Test group with empty name"""
        with pytest.raises(ValidationError) as exc_info:
            GroupCreate(group_name="")
        
        assert "group_name" in str(exc_info.value).lower()


class TestTimecardSchemas:
    """Test timecard-related schemas"""
    
    def test_timecard_create_valid(self):
        """Test valid timecard creation"""
        from datetime import time
        
        timecard = TimecardCreate(
            day_of_week=0,  # Monday
            time_from=time(8, 0),
            time_to=time(16, 0)
        )
        
        assert timecard.day_of_week == 0
        assert timecard.time_from.hour == 8
        assert timecard.time_to.hour == 16
    
    def test_timecard_invalid_day(self):
        """Test timecard with invalid day of week"""
        from datetime import time
        
        with pytest.raises(ValidationError) as exc_info:
            TimecardCreate(
                day_of_week=7,  # Invalid, should be 0-6
                time_from=time(8, 0),
                time_to=time(16, 0)
            )
        
        assert "day_of_week" in str(exc_info.value).lower()
