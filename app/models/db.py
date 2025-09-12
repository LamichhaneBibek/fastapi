from sqlalchemy import DateTime, Enum, Integer, String, Boolean, UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql.functions import current_time, current_timestamp

from app.models import enums

Base = declarative_base()


class UserDB(Base):
    __tablename__ = "users"

    id = mapped_column("id", UUID, primary_key=True)
    name = mapped_column("name", String)
    email = mapped_column("email", String, unique=True)
    password = mapped_column("password", String)
    role = mapped_column("role", Enum(enums.UserRole), default=enums.UserRole.USER)
    phone = mapped_column("phone", String)
    is_active = mapped_column("is_active", Boolean, default=False, nullable=False)
    email_verification_token = mapped_column("email_verification_token", String, nullable=True)
    updated_at = mapped_column(
        "updated_at",
        DateTime(),
        server_default=current_timestamp(),
        server_onupdate=current_time(),
    )
    created_at = mapped_column(
        "created_at", DateTime(), server_default=current_timestamp()
    )
