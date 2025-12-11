"""
FastAPI test configuration and fixtures
"""
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set test environment before importing app
os.environ["APP_ENV"] = "test"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from src.main import app
from src.database import Base, get_db
from src.auth_utils import get_password_hash


# Create test database engine
TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=test_engine)
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session):
    """
    Create a test client with a fresh database for each test
    """
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """Sample user data for testing"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
        "first_name": "Test",
        "second_name": "User"
    }


@pytest.fixture
def test_user(db_session, test_user_data):
    """Create a test user in the database"""
    from src.data.models import User
    
    user = User(
        username=test_user_data["username"],
        email=test_user_data["email"],
        password=get_password_hash(test_user_data["password"]),
        first_name=test_user_data.get("first_name"),
        second_name=test_user_data.get("second_name"),
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(client, test_user, test_user_data):
    """Get authentication headers with valid JWT token"""
    # Login to get token
    response = client.post(
        "/auth/login",
        data={
            "username": test_user_data["email"],
            "password": test_user_data["password"]
        }
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    return {"Authorization": f"Bearer {token}"}
