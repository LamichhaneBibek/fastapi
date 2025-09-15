from random import randint
import secrets
from typing import Optional
from uuid import UUID
import uuid
import re
import logging
from datetime import datetime, timezone

from sqlalchemy.orm.dynamic import AppenderMixin
from app.models import db
from app.models import dto
from app.models import enums
from app.repos import user_repo
from fastapi import BackgroundTasks
from app.core.security import bcrypt_hashing
from app.utils import formatting
from app.mappers import user_mapper
from app.exceptions.scheme import AppException
from app.utils.email import send_verification_email  # Import the function

MIN_PASS = 100000
MAX_PASS = 999999
logger = logging.getLogger(__name__)




def get_all(limit: int = 1000, offset: int = 0) -> list[dto.UserDTO]:
    return [user_mapper.db_to_get_dto(user) for user in user_repo.get(limit, offset)]


def get_by_id(id: UUID) -> db.UserDB:
    user = user_repo.get_by_id(id)
    if user is None:
        raise AppException(message="User not found", status_code=404)

    return user


def get_by_id_dto(id: UUID) -> dto.UserDTO:
    user = get_by_id(id)
    return user_mapper.db_to_get_dto(user)


def get_by_email(email: str) -> Optional[db.UserDB]:
    """Get user by email with validation"""
    if not email:
        return None

    email_formatted = formatting.format_string(email)
    if not _is_valid_email(email_formatted):
        return None

    return user_repo.get_by_email(email_formatted)


def get_by_email_dto(email: str) -> dto.UserDTO:
    user = get_by_email(email)
    return user_mapper.db_to_get_dto(user)


def create_user(obj: dto.UserCreateDTO, background_tasks: BackgroundTasks) -> dto.UserDTO:
    """Create user with comprehensive validation and error handling"""

    # 1. Input validation and sanitization
    email_formatted = formatting.format_string(obj.email)
    if not email_formatted or not _is_valid_email(email_formatted):
        raise AppException(message="Email is not valid", status_code=422)

    name_formatted = formatting.format_string(obj.name)
    if not name_formatted or len(name_formatted) < 2:
        raise AppException(message="Name must be at least 2 characters", status_code=422)

    # 2. Password validation
    if not _is_valid_password(obj.password):
        raise AppException(
            message="Password must be at least 8 characters with uppercase, lowercase, number, and special character",
            status_code=422
        )

    # 3. Business logic validation
    existing_user = user_repo.get_by_email(email_formatted)
    if existing_user is not None:
        # Log potential security issue
        logger.warning(f"Registration attempt with existing email: {email_formatted}")
        raise AppException(message="Email already exists", status_code=422)

    # 4. Generate secure verification token
    verification_token = secrets.token_urlsafe(32)

    # 5. Queue background email (non-blocking)
    try:
        background_tasks.add_task(
            send_verification_email,
            to_email=email_formatted,
            token=verification_token
        )
        logger.info(f"Verification email for {email_formatted} queued")
    except Exception as e:
        # Don't fail user creation if email queuing fails
        logger.error(f"Failed to queue verification email: {str(e)}")
        raise AppException(message="Failed to queue verification email: {str(e)}", status_code=500)

    # 6. Create user in database with transaction
    try:
        user = _create(obj, enums.UserRole.USER, verification_token)
        logger.info(f"User created successfully: {user.email}")
        return user_mapper.db_to_get_dto(user)
    except Exception as e:
        logger.error(f"Failed to create user: {str(e)}")
        raise AppException(message="Account creation failed. Please try again later.", status_code=500)


def create_admin(obj: dto.UserCreateDTO) -> dto.UserDTO:
    user = _create(obj, enums.UserRole.ADMIN, "")
    return user_mapper.db_to_get_dto(user)


def update_name(user: db.UserDB, obj: dto.UserUpdateNameDTO) -> None:
    user.name = formatting.format_string(obj.name)
    user_repo.update(user)


def update_password(user: dto.UserDTO, obj: dto.UserUpdatePasswordDTO) -> None:
    user_db = get_by_id(user.id)
    if bcrypt_hashing.validate(obj.old_password, user_db.password) is False:
        raise AppException(message="Incorrect password", status_code=422)

    _update_password(user_db, obj.new_password)


def reset_password(email: str) -> None:
    user = get_by_email(email)
    new_pass = _reset_password(user)
    print(f"New password for {user.email} is '{new_pass}'")


def delete(id: UUID) -> None:
    user_repo.delete(id)


def _create(obj: dto.UserCreateDTO, role: enums.UserRole,  verification_token: str) -> db.UserDB:
    """Create user database record with validation"""

    # Additional validation before DB creation
    if not verification_token:
        raise ValueError("Verification token is required")

    try:
        user_to_db = db.UserDB()
        user_to_db.id = uuid.uuid4()
        user_to_db.name = formatting.format_string(obj.name)
        user_to_db.role = role
        user_to_db.email = formatting.format_string(obj.email)
        user_to_db.is_active = False
        user_to_db.password = bcrypt_hashing.hash(obj.password)
        user_to_db.email_verification_token = verification_token
        user_to_db.created_at = datetime.now(timezone.utc)

        return user_repo.add(user_to_db)
    except Exception as e:
        logger.error(f"Database error creating user: {str(e)}")
        raise


def _update_password(user: db.UserDB, new_password: str) -> None:
    new_pass_hash = bcrypt_hashing.hash(new_password)
    user.password = new_pass_hash
    user_repo.update(user)


def _reset_password(user: db.UserDB) -> str:
    new_password = str(randint(MIN_PASS, MAX_PASS))
    _update_password(user, new_password)

    return new_password

def verify_email(token: str) -> bool:
    """Verify user email with comprehensive validation"""

    # 1. Token validation
    if not token or len(token) < 20:
        raise AppException(message="Invalid verification token", status_code=400)

    # 2. Find user by token
    user = user_repo.get_by_verification_token(token)
    if user is None:
        logger.warning(f"Email verification attempted with invalid token: {token[:10]}...")
        raise AppException(message="Invalid or expired verification token", status_code=404)

    # 3. Check if already verified
    if user.is_active:
        raise AppException(message="Email already verified", status_code=400)

    # 4. Verify user
    try:
        user.is_active = True
        user.email_verification_token = None  # Clear token
        user.updated_at = datetime.now(timezone.utc)

        user_repo.update(user)
        logger.info(f"Email verified successfully for user: {user.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to verify email: {str(e)}")
        raise AppException(message="Email verification failed", status_code=500)


def _is_valid_email(email: str) -> bool:
    """Validate email format"""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, email))

def _is_valid_password(password: str) -> bool:
    """Validate password strength"""
    if len(password) < 8:
        return False

    # Check for at least one uppercase, lowercase, number, and special character
    has_upper = bool(re.search(r'[A-Z]', password))
    has_lower = bool(re.search(r'[a-z]', password))
    has_digit = bool(re.search(r'\d', password))
    has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))

    return all([has_upper, has_lower, has_digit, has_special])
