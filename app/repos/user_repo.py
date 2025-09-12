from uuid import UUID
from app.models.db import UserDB
from app.core.db_context import session_maker


def add(user: UserDB)-> UserDB:
    with session_maker.begin() as session:
        session.add(user)
        return user


def get_by_verification_token(token: str) -> UserDB:
    """Get user by email verification token"""
    with session_maker() as session:
        return session.query(UserDB).filter(
            UserDB.email_verification_token == token
        ).first()

def update(user: UserDB) -> UserDB:
    """Update user in database"""
    with session_maker.begin() as session:
        session.merge(user)
        return user
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

def get_by_email(email: str) -> UserDB | None:
    with session_maker.begin() as session:
        return session.query(UserDB).where(
            UserDB.email == email
        ).first()
