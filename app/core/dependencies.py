from typing import Annotated
from models import dto
from fastapi import Depends
from core.security import session


token_dependency = Annotated[dto.Token, Depends(session.get_token)]
user_dependency = Annotated[dto.UserDTO, Depends(session.get_user)]
admin_dependency = Annotated[dto.UserDTO, Depends(session.get_admin)]