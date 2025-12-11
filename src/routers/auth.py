from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from ..database import get_db
from ..schemas import UserCreate, UserResponse, UserLogin, Token, PasswordResetRequest, MessageResponse
from ..auth_utils import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_active_user
)
from ..config import settings
from ..data.models import User

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user
    """
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password=hashed_password,
        first_name=user_data.first_name,
        second_name=user_data.second_name
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login and get access token
    
    The OAuth2PasswordRequestForm expects:
    - username (we'll use email)
    - password
    """
    # Find user by email (using username field from form)
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """
    Get current authenticated user information
    """
    return current_user


@router.post("/logout")
async def logout():
    """
    Logout (with JWT, this is mainly client-side - delete token)
    """
    return {"message": "Successfully logged out. Please delete your token on the client side."}


@router.post("/password-reset-request", response_model=MessageResponse)
async def request_password_reset(
    request_data: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """
    Request password reset - sends email with reset token
    """
    user = db.query(User).filter(User.email == request_data.email).first()
    
    if not user:
        # Don't reveal that user doesn't exist
        return {"message": "If the email exists, a password reset link has been sent"}
    
    # TODO: Implement password reset token generation and email sending
    # For now, return success message
    return {"message": "If the email exists, a password reset link has been sent"}
