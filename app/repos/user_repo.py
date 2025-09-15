from uuid import UUID
from app.models.db import UserDB
import logging
from app.exceptions.scheme import AppException
from app.core.db_context import session_maker
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

logger = logging.getLogger(__name__)


def add(user: UserDB) -> UserDB:
    """Add user with proper error handling"""
    try:
        with session_maker.begin() as session:
            session.add(user)
            session.flush()  # Flush to get any constraint violations
            return user
    except IntegrityError as e:
        logger.error(f"Database integrity error: {str(e)}")
        if "email" in str(e):
            raise AppException(message="Email already exists", status_code=422)
        else:
            raise AppException(message="Database constraint violation", status_code=422)
    except SQLAlchemyError as e:
        logger.error(f"Database error in add_user: {str(e)}")
        raise AppException(message="Database error occurred", status_code=500)



def get_by_verification_token(token: str) -> UserDB:
    """Get user by email verification token"""
    try:
        with session_maker() as session:
            return session.query(UserDB).filter(
                UserDB.email_verification_token == token
            ).first()
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_by_verification_token: {str(e)}")
        raise AppException(message="Database error occurred", status_code=500)


def update(user: UserDB) -> UserDB:
    """Update user in database"""
    try:
        with session_maker.begin() as session:
            session.merge(user)
            return user
    except SQLAlchemyError as e:
        logger.error(f"Database error in update_user: {str(e)}")
        raise AppException(message="Failed to update user", status_code=500)


# def update(user: UserDB) -> None:
#     with session_maker.begin() as session:
#         session.query(UserDB).filter(UserDB.id == user.id).update({
#             UserDB.name: user.name,
#             UserDB.role: user.role,
#             UserDB.email: user.email,
#             UserDB.password: user.password,
#             UserDB.is_active: user.is_active,
#             UserDB.email_verification_token: user.email_verification_token
#         })

def delete(id: UUID) -> None:
    with session_maker.begin() as session:
        session.query(UserDB).filter(UserDB.id == id).delete()

def get(limit:int = 1000, offset: int = 0) -> list[UserDB]:
    with session_maker() as session:
        return session.query(UserDB).limit(limit).offset(offset).all()

def get_by_id(id: UUID) -> UserDB | None:
    with session_maker() as session:
        return session.query(UserDB).where(
            UserDB.id == id
        ).first()

def get_by_email(email: str) -> UserDB:
    """Get user by email"""
    try:
        with session_maker() as session:
            return session.query(UserDB).filter(
                UserDB.email == email
            ).first()
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_by_email: {str(e)}")
        raise AppException(message="Database error occurred", status_code=500)
