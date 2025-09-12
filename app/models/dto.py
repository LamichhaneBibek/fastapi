from ssl import OP_ENABLE_MIDDLEBOX_COMPAT
from pydantic import Field, BaseModel
from datetime import datetime
from uuid import UUID

from app.models.enums import UserRole


class UserCreateDTO(BaseModel):
    name: str
    email: str
    password: str = Field(..., min_length=6)


class UserDTO(BaseModel):
    id: UUID
    name: str
    email: str
    role: UserRole
    is_active: bool
    updated_at: datetime
    created_at: datetime


class UserUpdateNameDTO(BaseModel):
    name: str


class UserLoginDTO(BaseModel):
    email: str
    password: str = Field(..., min_length=6)


class UserUpdatePasswordDTO(BaseModel):
    old_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6)

class Token(BaseModel):
    user_id: UUID
    role: str
