from datetime import datetime
from fastapi.requests import Request
from core.templates import templates
from models.dto import UserDTO


def main_page(request: Request):
    now = datetime.now()
    return templates.TemplateResponse(
        request, "main.jinja", {"date": now.replace(microsecond=0)}
    )


def auth_page(
    request: Request,
    user: UserDTO
):
    return templates.TemplateResponse(
        request, "auth.jinja", {"user": user}
    )
