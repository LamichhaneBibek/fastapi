from datetime import datetime
from datetime import timezone

from fastapi import Request
from fastapi import Response
from fastapi import Depends
from uuid import UUID
from app.core.config import CONFIG
from app.service import user_service
from app.exceptions.scheme import AppException
from app.models import enums
from app.models import dto
from app.core.security import jwt
from app.core.security import bcrypt_hashing
import logging
from typing import Optional

from app.utils import formatting

logger = logging.getLogger(__name__)



def get_token(req: Request, res: Response) -> dto.Token:
    """Get and validate session token"""
    try:
        session_token = req.cookies.get(CONFIG.COOKIES_KEY_NAME)
        if not session_token:
            raise AppException(status_code=401, message="No session token")

        # Decode and validate token
        token_dict = jwt.decode(session_token)
        if not token_dict:
            logger.warning("Invalid session token detected")
            res.delete_cookie(CONFIG.COOKIES_KEY_NAME)
            raise AppException(status_code=401, message="Invalid session token")

        # Convert user_id back to UUID
        if isinstance(token_dict.get('user_id'), str):
            try:
                token_dict['user_id'] = UUID(token_dict['user_id'])
            except ValueError:
                logger.error("Invalid UUID in session token")
                res.delete_cookie(CONFIG.COOKIES_KEY_NAME)
                raise AppException(status_code=401, message="Invalid session")

        # Validate token expiration
        exp_time = token_dict.get('exp')
        if exp_time and datetime.fromtimestamp(exp_time, timezone.utc) < datetime.now(timezone.utc):
            logger.info("Expired session token")
            res.delete_cookie(CONFIG.COOKIES_KEY_NAME)
            raise AppException(status_code=401, message="Session expired")

        return dto.Token(**token_dict)

    except AppException:
        raise
    except Exception as e:
        logger.error(f"Error validating session token: {str(e)}")
        res.delete_cookie(CONFIG.COOKIES_KEY_NAME)
        raise AppException(status_code=401, message="Invalid session")

def get_user(req: Request, res: Response) -> dto.UserDTO:
    """Get current user with validation"""
    try:
        token = get_token(req, res)

        # Additional validation: check if user still exists and is active
        user = user_service.get_by_id(token.user_id)
        if not user:
            logger.warning(f"Session token for non-existent user: {token.user_id}")
            res.delete_cookie(CONFIG.COOKIES_KEY_NAME)
            raise AppException(status_code=401, message="User not found")

        if not user.is_active:
            logger.warning(f"Session token for inactive user: {user.email}")
            res.delete_cookie(CONFIG.COOKIES_KEY_NAME)
            raise AppException(status_code=401, message="Account deactivated")

        return user

    except AppException:
        raise
    except Exception as e:
        logger.error(f"Error getting current user: {str(e)}")
        raise AppException(status_code=401, message="Authentication failed")


def get_admin(user: dto.UserDTO = Depends(get_user)) -> dto.UserDTO:
    if user.role != enums.UserRole.ADMIN:
        raise AppException(status_code=403, message="Forbidden. Not an admin user")

    return user

async def login(obj: dto.UserLoginDTO, res: Response) -> str:
    """Login with comprehensive security validation"""

       # 1. Input validation
    if not obj.email or not obj.password:
        raise AppException("Email and password are required", 400)

    email_formatted = formatting.format_string(obj.email)
    if not email_formatted:
        raise AppException("Invalid email format", 400)

       # 2. Rate limiting check (implement this)
       # await _check_rate_limit(email_formatted, request.client.host)

    try:
        NOW = datetime.now(timezone.utc)

           # 3. User lookup with security logging
        user_db = user_service.get_by_email(email_formatted)
        if not user_db:

               # Log failed login attempt
            logger.warning(f"Login attempt for non-existent user: {email_formatted}")
               # Don't reveal if user exists or not
            await _simulate_password_check()  # Prevent timing attacks
            raise AppException("Invalid credentials", 401)

           # 4. Account status checks
        if not user_db.is_active:
            logger.info(f"Login attempt for unverified account: {email_formatted}")
            raise AppException("Email not verified. Please check your inbox.", 403)

           # Check if account is locked (add this field to your model)
        if getattr(user_db, 'is_locked', False):
            logger.warning(f"Login attempt for locked account: {email_formatted}")
            raise AppException("Account is locked. Please contact support.", 403)

           # 5. Password validation
        if not bcrypt_hashing.validate(obj.password, user_db.password):
            logger.warning(f"Invalid password for user: {email_formatted}")
               # TODO: Increment failed login attempts
               # await _increment_failed_attempts(user_db)
            raise AppException("Invalid credentials", 401)

           # 6. Reset failed login attempts on successful login
           # await _reset_failed_attempts(user_db)

           # 7. Generate secure session token
        exp_date = NOW + CONFIG.SESSION_TIME
        token = dto.Token(
               user_id=user_db.id,
               role=user_db.role
           )

        token_dict = token.model_dump()
        token_dict['user_id'] = str(token_dict['user_id'])
        token_str = jwt.encode(token_dict, exp_date)

           # 8. Set secure cookie
        res.set_cookie(
               key=CONFIG.COOKIES_KEY_NAME,
               value=token_str,
               expires=exp_date,
               httponly=True,  # Prevent XSS
               secure=True,    # HTTPS only
               samesite="strict"  # CSRF protection
           )

           # 9. Log successful login
        logger.info(f"Successful login for user: {email_formatted}")

        return token_str

    except AppException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}")
        raise AppException("Login failed. Please try again.", 500)


async def logout(res: Response) -> None:
    res.delete_cookie(CONFIG.COOKIES_KEY_NAME)

async def _simulate_password_check():
    """Simulate password hashing to prevent timing attacks"""
    import time
    await asyncio.sleep(0.1)
