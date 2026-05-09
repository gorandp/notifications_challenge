import os

from app.external.fastapi_app.main import app as app

from app.core.logger import LoggerConfig
from app.external.database.database import Database
from app.external.fastapi_app.context import init_context
from app.external.database.database_models import Base as DatabaseBaseModel
from app.external.fastapi_app.config import JWTConfig


LoggerConfig.set_level(os.getenv("LOGGER_LEVEL", "INFO"))
JWTConfig.set_secret(os.getenv("JWT_SECRET", "SECRET_NOT_SET_UNSECURE"))
database = Database({"url": os.getenv("DB_CONNECTION_STRING", "sqlite:///./dev.db")})
# Create tables if not exist
DatabaseBaseModel.metadata.create_all(bind=database.engine)
init_context(database)
