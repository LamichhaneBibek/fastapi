from random import randint
import secrets
from uuid import UUID
import uuid
import logging
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


def get_by_email(email: str) -> db.UserDB:
    email_form = formatting.format_string(email)
    user = user_repo.get_by_email(email_form)
    if user is None:
        raise AppException(message="User not found", status_code=404)

    return user


def get_by_email_dto(email: str) -> dto.UserDTO:
    user = get_by_email(email)
    return user_mapper.db_to_get_dto(user)


def create_user(obj: dto.UserCreateDTO, background_tasks: BackgroundTasks) -> dto.UserDTO:
    name_formatted = formatting.format_string(obj.name)
    email_formatted = formatting.format_string(obj.email)

    if name_formatted == "":
        raise AppException(message="Name is not valid", status_code=422)

    if email_formatted == "":
        raise AppException(message="Email is not valid", status_code=422)

    if user_repo.get_by_email(email_formatted) is not None:
        raise AppException(message="Email already exists", status_code=422)

    verification_token = secrets.token_urlsafe(32)

    background_tasks.add_task(
        send_verification_email, 
        to_email=email_formatted, 
        token=verification_token
    )
    logger.info(f"Verification email for {email_formatted} queued to be sent in the background.")
    
    try:
        user = _create(obj, enums.UserRole.USER, verification_token)
        logger.info(f"User created successfully: {user.email}")
        return user_mapper.db_to_get_dto(user)
    except Exception as e:
        # Note: If user creation fails, the email might still be sent.
        # This is often an acceptable trade-off for performance.
        # For more critical systems, a more robust task queue like Celery might be needed.
        logger.error(f"Failed to create user after queuing email: {str(e)}")
        raise AppException(message="Account creation failed. Please contact support.", status_code=500)


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
    user_to_db = db.UserDB()
    user_to_db.id = uuid.uuid4()
    user_to_db.name = formatting.format_string(obj.name)
    user_to_db.role = role
    user_to_db.email = formatting.format_string(obj.email)
    user_to_db.is_active = False
    user_to_db.password = bcrypt_hashing.hash(obj.password)
    user_to_db.email_verification_token = verification_token
    return user_repo.add(user_to_db)


def _update_password(user: db.UserDB, new_password: str) -> None:
    new_pass_hash = bcrypt_hashing.hash(new_password)
    user.password = new_pass_hash
    user_repo.update(user)


def _reset_password(user: db.UserDB) -> str:
    new_password = str(randint(MIN_PASS, MAX_PASS))
    _update_password(user, new_password)

    return new_password

def verify_email(token: str) -> bool:
    """Verify user email with token"""
    user = user_repo.get_by_verification_token(token)
    if not user:
        return False

    # Activate the user and clear the token
    user.is_active = True
    user.email_verification_token = None
    user_repo.update(user)

    return True
