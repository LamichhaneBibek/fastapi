from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from app.core.config import CONFIG

def add(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[CONFIG.FRONTEND_URL],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
