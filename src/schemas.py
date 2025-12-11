from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from typing import Optional
from datetime import datetime, time


# User schemas
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    first_name: Optional[str] = None
    second_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    second_name: Optional[str] = None


class UserResponse(UserBase):
    id: int
    first_name: Optional[str] = None
    second_name: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None


# Password reset schemas
class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordReset(BaseModel):
    token: str
    new_password: str = Field(..., min_length=6)


# Card schemas
class CardBase(BaseModel):
    card_number: str = Field(..., pattern=r"^\d+$")
    chip_number: Optional[str] = Field(None, pattern=r"^[a-fA-F0-9]+$")


class CardCreate(CardBase):
    pass


class CardResponse(CardBase):
    id: int
    user_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


# Group schemas
class GroupBase(BaseModel):
    group_name: str = Field(..., min_length=1, max_length=100)


class GroupCreate(GroupBase):
    pass


class GroupUpdate(BaseModel):
    group_name: Optional[str] = Field(None, min_length=1, max_length=100)


class GroupResponse(GroupBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# Timecard schemas
class TimecardBase(BaseModel):
    day_of_week: int = Field(..., ge=0, le=6)  # 0=Monday, 6=Sunday
    time_from: time
    time_to: time


class TimecardCreate(TimecardBase):
    pass


class TimecardResponse(TimecardBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# File upload schema
class FileUpload(BaseModel):
    filename: str

    @field_validator('filename')
    @classmethod
    def validate_extension(cls, v):
        if not v.endswith('.xml'):
            raise ValueError('Only XML files are allowed')
        return v


# Month selection schema
class MonthSelection(BaseModel):
    month: str = Field(..., pattern=r"^\d{4}-\d{2}$")  # Format: YYYY-MM
    group_id: int


# Generic response schemas
class MessageResponse(BaseModel):
    message: str
    detail: Optional[str] = None


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
