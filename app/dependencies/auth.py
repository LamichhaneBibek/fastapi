# app/dependencies/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from app.core.config import CONFIG

api_key_header = APIKeyHeader(name=CONFIG.API_KEY_NAME, auto_error=False)

async def get_api_key(api_key: str = Depends(api_key_header)):
    if api_key != CONFIG.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key"
        )
    return api_key
