from fastapi.requests import Request
from exceptions.scheme import AppException
from core.templates import templates


def error_page(request: Request, exc: AppException):
    return templates.TemplateResponse(
        request, "error.jinja", {"message": exc.message, "status_code": exc.status_code}
    )
