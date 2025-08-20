from enum import StrEnum
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass


class UserRole(StrEnum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"
