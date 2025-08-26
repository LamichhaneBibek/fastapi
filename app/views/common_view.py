from fastapi.requests import Request
from app.exceptions.scheme import AppException
from app.core.templates import templates


def error_page(request: Request, exc: AppException):
    return templates.TemplateResponse(
        request, "error.jinja", {"message": exc.message, "status_code": exc.status_code}
    )
