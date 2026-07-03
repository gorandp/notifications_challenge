from fastapi import Request
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.external.fastapi_app.main import app as app

from app.core.logger import LoggerConfig
from app.external.database.database import Database
from app.external.fastapi_app.context import (
    init_context,
    db_session,
    database_ctx,
)
from app.external.database.database_models import Base as DatabaseBaseModel
from app.external.fastapi_app.config import JWTConfig


class Settings(BaseSettings):
    DB_CONNECTION_STRING: str = "sqlite:///./dev.db"
    JWT_SECRET: str = "SECRET_NOT_SET_UNSECURE"
    LOGGER_LEVEL: str = "INFO"

    # Tell Pydantic to read from a .env file
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()


LoggerConfig.set_level(settings.LOGGER_LEVEL)
JWTConfig.set_secret(settings.JWT_SECRET)
database = Database({"url": settings.DB_CONNECTION_STRING})
# Create tables if not exist
DatabaseBaseModel.metadata.create_all(bind=database.engine)
init_context(database)


@app.middleware("http")
async def set_db_session(request: Request, call_next):
    db = database_ctx.get()
    with db.session_local() as session:
        token = db_session.set(session)
        response = await call_next(request)
        db_session.reset(token)
    return response
