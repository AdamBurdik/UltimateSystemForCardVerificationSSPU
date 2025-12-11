"""
Tests for FastAPI authentication endpoints
"""
import pytest
from test.test_fastapi_conftest import client, db_session, test_user_data, test_user, auth_headers


class TestAuthRegistration:
    """Test user registration endpoint"""
    
    def test_register_new_user(self, client, db_session):
        """Test successful user registration"""
        response = client.post(
            "/auth/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "securepassword123",
                "first_name": "New",
                "second_name": "User"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert "password" not in data  # Password should not be in response
        assert "id" in data
    
    def test_register_duplicate_username(self, client, test_user):
        """Test registration with existing username"""
        response = client.post(
            "/auth/register",
            json={
                "username": test_user.username,
                "email": "different@example.com",
                "password": "password123"
            }
        )
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
    
    def test_register_duplicate_email(self, client, test_user):
        """Test registration with existing email"""
        response = client.post(
            "/auth/register",
            json={
                "username": "differentuser",
                "email": test_user.email,
                "password": "password123"
            }
        )
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
    
    def test_register_invalid_email(self, client):
        """Test registration with invalid email format"""
        response = client.post(
            "/auth/register",
            json={
                "username": "testuser",
                "email": "not-an-email",
                "password": "password123"
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_register_short_password(self, client):
        """Test registration with password too short"""
        response = client.post(
            "/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "short"
            }
        )
        
        assert response.status_code == 422  # Validation error


class TestAuthLogin:
    """Test user login endpoint"""
    
    def test_login_success(self, client, test_user, test_user_data):
        """Test successful login"""
        response = client.post(
            "/auth/login",
            data={
                "username": test_user_data["email"],  # OAuth2 uses 'username' field
                "password": test_user_data["password"]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0
    
    def test_login_wrong_password(self, client, test_user, test_user_data):
        """Test login with incorrect password"""
        response = client.post(
            "/auth/login",
            data={
                "username": test_user_data["email"],
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()
    
    def test_login_nonexistent_user(self, client):
        """Test login with non-existent email"""
        response = client.post(
            "/auth/login",
            data={
                "username": "nonexistent@example.com",
                "password": "anypassword"
            }
        )
        
        assert response.status_code == 401
    
    def test_login_inactive_user(self, client, db_session, test_user_data):
        """Test login with inactive user"""
        from src.data.models import User
        from src.auth_utils import get_password_hash
        
        # Create inactive user
        inactive_user = User(
            username="inactive",
            email="inactive@example.com",
            password=get_password_hash("password123"),
            is_active=False
        )
        db_session.add(inactive_user)
        db_session.commit()
        
        response = client.post(
            "/auth/login",
            data={
                "username": "inactive@example.com",
                "password": "password123"
            }
        )
        
        assert response.status_code == 400
        assert "inactive" in response.json()["detail"].lower()


class TestAuthProtected:
    """Test protected endpoints requiring authentication"""
    
    def test_get_current_user(self, client, auth_headers, test_user):
        """Test getting current user info with valid token"""
        response = client.get("/auth/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == test_user.username
        assert data["email"] == test_user.email
        assert "password" not in data
    
    def test_get_current_user_no_token(self, client):
        """Test accessing protected endpoint without token"""
        response = client.get("/auth/me")
        
        assert response.status_code == 401
    
    def test_get_current_user_invalid_token(self, client):
        """Test accessing protected endpoint with invalid token"""
        response = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid-token"}
        )
        
        assert response.status_code == 401


class TestAuthLogout:
    """Test logout endpoint"""
    
    def test_logout(self, client, auth_headers):
        """Test logout (client-side token deletion)"""
        response = client.post("/auth/logout", headers=auth_headers)
        
        assert response.status_code == 200
        assert "logged out" in response.json()["message"].lower()


class TestPasswordReset:
    """Test password reset functionality"""
    
    def test_request_password_reset(self, client, test_user):
        """Test requesting password reset"""
        response = client.post(
            "/auth/password-reset-request",
            json={"email": test_user.email}
        )
        
        assert response.status_code == 200
        assert "message" in response.json()
    
    def test_request_password_reset_nonexistent(self, client):
        """Test password reset for non-existent email (should not reveal)"""
        response = client.post(
            "/auth/password-reset-request",
            json={"email": "nonexistent@example.com"}
        )
        
        # Should return success to avoid email enumeration
        assert response.status_code == 200


class TestHealthCheck:
    """Test health check endpoint"""
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestAPIDocumentation:
    """Test API documentation endpoints"""
    
    def test_openapi_schema(self, client):
        """Test OpenAPI schema is accessible"""
        response = client.get("/openapi.json")
        
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "paths" in data
    
    def test_swagger_docs(self, client):
        """Test Swagger UI is accessible"""
        response = client.get("/api/docs")
        
        assert response.status_code == 200
        assert b"swagger" in response.content.lower()
    
    def test_redoc(self, client):
        """Test ReDoc is accessible"""
        response = client.get("/api/redoc")
        
        assert response.status_code == 200
        assert b"redoc" in response.content.lower()
