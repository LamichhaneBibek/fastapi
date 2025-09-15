from ssl import OP_ENABLE_MIDDLEBOX_COMPAT
from pydantic import Field, BaseModel, EmailStr, field_validator
from datetime import datetime
from uuid import UUID
import re

from app.models.enums import UserRole


class UserCreateDTO(BaseModel):
    """User creation DTO with comprehensive validation"""
    name: str = Field(..., min_length=2, max_length=100, description="User's full name")
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, max_length=128, description="User's password")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        # Remove extra whitespace
        v = v.strip()

        # Check for valid characters (letters, spaces, hyphens, apostrophes)
        if not re.match(r"^[a-zA-Z\s\-']+$", v):
            raise ValueError("Name can only contain letters, spaces, hyphens, and apostrophes")

        # Check for at least one letter
        if not re.search(r'[a-zA-Z]', v):
            raise ValueError("Name must contain at least one letter")

        return v

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: EmailStr) -> EmailStr:
        # Convert to lowercase and strip whitespace
        email_str = str(v).lower().strip()

        # Additional email validation beyond EmailStr
        if len(email_str) > 254:  # RFC 5321 limit
            raise ValueError("Email address is too long")

        # Check for common disposable email domains (optional)
        disposable_domains = ['tempmail.com', '10minutemail.com', 'guerrillamail.com']
        domain = email_str.split('@')[1]
        if domain in disposable_domains:
            raise ValueError("Disposable email addresses are not allowed")

        return (email_str)

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        # Check password strength
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")

        # Check for required character types
        checks = {
            'uppercase': bool(re.search(r'[A-Z]', v)),
            'lowercase': bool(re.search(r'[a-z]', v)),
            'digit': bool(re.search(r'\d', v)),
            'special': bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', v))
        }

        missing = [key for key, check in checks.items() if not check]
        if missing:
            raise ValueError(f"Password must contain: {', '.join(missing)} characters")

        # Check for common weak passwords
        weak_passwords = ['password', '12345678', 'qwerty', 'admin']
        if v.lower() in weak_passwords:
            raise ValueError("Password is too common. Please choose a stronger password")

        return v

class UserDTO(BaseModel):
    id: UUID
    name: str
    email: str
    role: UserRole
    is_active: bool
    updated_at: datetime
    created_at: datetime


class UserUpdateNameDTO(BaseModel):
    name: str


class UserLoginDTO(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserUpdatePasswordDTO(BaseModel):
    old_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6)

class Token(BaseModel):
    user_id: UUID
    role: str
