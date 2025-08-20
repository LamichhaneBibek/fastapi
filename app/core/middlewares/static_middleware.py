from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI


def add(app: FastAPI):
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
