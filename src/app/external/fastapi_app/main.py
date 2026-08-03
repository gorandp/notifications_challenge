from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic_settings import BaseSettings, SettingsConfigDict

from .routers import auth, users, notifications, channels, settings

# from app.external.database.database_models import Base as DatabaseBaseModel
from app.core.logger import LoggerConfig
from app.external.database.database import Database
from app.external.fastapi_app.context import init_context
from app.external.fastapi_app.config import JWTConfig


class Settings(BaseSettings):
    DB_CONNECTION_STRING: str = (
        "postgresql+psycopg://notifuser:notifpass@localhost:5432/notifdb"
    )
    JWT_SECRET: str = "SECRET_NOT_SET_UNSECURE"
    LOGGER_LEVEL: str = "INFO"

    # Tell Pydantic to read from a .env file
    model_config = SettingsConfigDict(env_file=".env")


env_settings = Settings()
LoggerConfig.set_level(env_settings.LOGGER_LEVEL)
JWTConfig.set_secret(env_settings.JWT_SECRET)
database = Database({"url": env_settings.DB_CONNECTION_STRING})
init_context(database)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Startup
    # async with database.engine.begin() as conn:
    #     # Delete tables if exist
    #     await conn.run_sync(DatabaseBaseModel.metadata.drop_all)
    #     # Create tables if not exist
    #     await conn.run_sync(DatabaseBaseModel.metadata.create_all)
    # Run
    yield
    # Shutdown
    await database.engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(
    auth.router,
    tags=["Auth"],
)
app.include_router(
    users.router,
    prefix="/users",
    tags=["Users"],
)
app.include_router(
    notifications.router,
    prefix="/notifications",
    tags=["Notifications"],
)
app.include_router(
    channels.router,
    prefix="/channels",
    tags=["Channels"],
)
app.include_router(
    settings.router,
    prefix="/settings",
    tags=["Settings"],
)


@app.get("/hello", tags=["Initial Test"])
async def home():
    return {"msg": "Hello World!"}


@app.exception_handler(StarletteHTTPException)
async def general_http_exception_handler(
    request: Request,
    exception: StarletteHTTPException,
):
    return await http_exception_handler(request, exception)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exception: RequestValidationError,
):
    return await request_validation_exception_handler(request, exception)
