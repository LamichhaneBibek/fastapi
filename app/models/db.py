from sqlalchemy import DateTime, Enum, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql.functions import current_time, current_timestamp

from models import enums

Base = declarative_base()


class UserDB(Base):
    __tablename__ = "users"

    id = mapped_column("id", Integer, primary_key=True, autoincrement=True)
    name = mapped_column("name", String)
    email = mapped_column("email", String, unique=True)
    password = mapped_column("password", String)
    role = mapped_column("role", Enum(enums.UserRole), default=enums.UserRole.USER)
    phone = mapped_column("phone", String)
    updated_at = mapped_column(
        "updated_at",
        DateTime(),
        server_default=current_timestamp(),
        server_onupdate=current_time(),
    )
    created_at = mapped_column(
        "created_at", DateTime(), server_default=current_timestamp()
    )
