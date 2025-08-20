from models.db import UserDB
from core.db_context import session_maker


def add(user: UserDB)-> UserDB:
    with session_maker.begin() as session:
        session.add(user)
        return user

def update(user: UserDB) -> None:
    with session_maker.begin() as session:
        session.query(UserDB).filter(UserDB.id == user.id).update({
            UserDB.name: user.name,
            UserDB.surname: user.surname,
            UserDB.role: user.role,
            UserDB.email: user.email,
            UserDB.password: user.password
        })

def delete(id: int) -> None:
    with session_maker.begin() as session:
        session.query(UserDB).filter(UserDB.id == id).delete()

def get(limit:int = 1000, offset: int = 0) -> list[UserDB]:
    with session_maker() as session:
        return session.query(UserDB).limit(limit).offset(offset).all()

def get_by_id(id: int) -> UserDB | None:
    with session_maker() as session:
        return session.query(UserDB).where(
            UserDB.id == id
        ).first()

def get_by_email(email: str) -> UserDB | None:
    with session_maker.begin() as session:
        return session.query(UserDB).where(
            UserDB.email == email
        ).first()
