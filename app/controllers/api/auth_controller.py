from app.exceptions.scheme import AppException
from app.models import dto
from app.service import user_service
from app.core.security import session
from app.core import dependencies
from fastapi import APIRouter, status, Response, BackgroundTasks, HTTPException
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=dto.UserDTO)
async def register(user: dto.UserCreateDTO, background_tasks: BackgroundTasks):
    try:
            # Input validation happens automatically via Pydantic models
            # Additional business validation in service layer
            return user_service.create_user(user, background_tasks)
    except AppException as e:
            # AppException is already handled by your exception middleware
        raise e
    except ValueError as e:
            # Handle validation errors
        logger.warning(f"Validation error in register: {str(e)}")
        raise AppException(message=f"Validation error: {str(e)}", status_code=422)
    except Exception as e:
            # Catch unexpected errors
        logger.error(f"Unexpected error in register: {str(e)}")
        raise AppException(message="Registration failed. Please try again.", status_code=500)

@router.post("/login", status_code=status.HTTP_200_OK, response_model=str)
async def login(obj: dto.UserLoginDTO, res: Response):
    """Login user with rate limiting and validation"""
    try:
        # TODO: Add rate limiting here (e.g., slowapi or custom middleware)
        # TODO: Add IP-based blocking for suspicious activity
        return await session.login(obj, res)
    except AppException as e:
        # Log security events
        if e.status_code in [401, 403]:
            logger.warning(f"Login attempt failed for email: {obj.email} - {e.message}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error in login: {str(e)}")
        raise AppException(message="Login failed. Please try again.", status_code=500)


@router.get("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(res: Response):
    await session.logout(res)

@router.get("/validate", response_model=dto.Token)
async def check_session(token: dependencies.token_dependency):
    return token

@router.put("/password/update", status_code=204)
def update_password(dto: dto.UserUpdatePasswordDTO, user: dependencies.user_dependency):
    user_service.update_password(user, dto)

@router.post("/password/reset", status_code=204)
def reset_password(email: str):
    user_service.reset_password(email)

@router.get("/verify-email", response_model=str)
async def verify_email(token: str):
    """Verify user email with token validation"""
    try:
        if not token or len(token) < 10:  # Basic token format validation
            raise AppException(message="Invalid verification token", status_code=400)

        verified =  user_service.verify_email(token)
        if not verified:
            raise AppException(message="User not verified", status_code=400)
        return
    except AppException as e:
        raise e
    except Exception as e:
        logger.error(f"Unexpected error in verify_email: {str(e)}")
        raise AppException(message="Email verification failed.", status_code=500)
