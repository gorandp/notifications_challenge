from workers import WorkerEntrypoint, Request
from sqlalchemy_cloudflare_d1 import create_engine_from_binding  # type: ignore
from sqlalchemy.orm import sessionmaker
from datetime import datetime, UTC
# from urllib.parse import urlparse

from app.logger import LogWrapper, LoggerConfig
from app.database_models import Base as DatabaseBaseModel
from app.fastapi_app.main import app as fastapi_app
from app.fastapi_app.database import db_session


class EntryLogger(LogWrapper):
    pass


class Default(WorkerEntrypoint):
    def __init__(self, ctx, env):
        super().__init__(ctx, env)
        LoggerConfig.set_level(self.env.LOGGER_LEVEL)
        self.logger = EntryLogger().logger
        engine = create_engine_from_binding(self.env.DB)
        self.SessionLocal = sessionmaker(bind=engine)
        DatabaseBaseModel.metadata.create_all(bind=engine)  # Create tables if not exist

    async def fetch(self, request: Request):
        # url = urlparse(request.url)
        # if url.path.startswith("/static"):
        #     return await self.env.ASSETS.fetch(request)

        import asgi

        with self.SessionLocal() as session:
            token = db_session.set(session)  # Store session for THIS request only
            try:
                return await asgi.fetch(
                    fastapi_app,
                    request.js_object,
                    self.env,
                )
            finally:
                db_session.reset(token)  # Clean up session after request
