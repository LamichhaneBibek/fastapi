from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from os import getenv
from dotenv import load_dotenv

load_dotenv()

def _get_from_env(var_name: str) -> str:
    value = getenv(var_name)
    if value is None:
        raise ValueError(f"Environment variable '{var_name}' must be set.")
    return value

@dataclass(frozen=True)
class Config:
    DB_CONNECTION_STRING: str
    COOKIES_KEY_NAME: str
    SESSION_TIME: timedelta
    HASH_SALT: str
    SERVICE_HOST: str
    SERVICE_PORT: int
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    DB_NAME: str

    @staticmethod
    def get_config() -> Config:
        db_connection_string = _get_from_env("DB_CONNECTION_STRING")
        cookies_key_name = _get_from_env("COOKIES_KEY_NAME")
        session_time = timedelta(days=1)
        hash_salt = _get_from_env("HASH_SALT")
        service_host = _get_from_env("SERVICE_HOST")
        service_port = int(_get_from_env("SERVICE_PORT"))
        postgres_host = _get_from_env("POSTGRES_HOST")
        postgres_port = int(_get_from_env("POSTGRES_PORT"))
        postgres_user = _get_from_env("POSTGRES_USER")
        postgres_password = _get_from_env("POSTGRES_PASSWORD")
        db_name = _get_from_env("DB_NAME")

        return Config(db_connection_string, cookies_key_name, session_time, hash_salt, service_host, service_port, postgres_host, postgres_port, postgres_user, postgres_password, db_name)

CONFIG = Config.get_config()