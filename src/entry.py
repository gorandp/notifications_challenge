from workers import WorkerEntrypoint, Request
from sqlalchemy_cloudflare_d1 import create_engine_from_binding
from sqlalchemy.orm import sessionmaker
# from urllib.parse import urlparse

from app.core.logger import LoggerConfig
from app.external.database.database import Database
from app.external.database.main import db_session, database_ctx
from app.external.database.database_models import Base as DatabaseBaseModel
from app.external.fastapi_app.main import app as fastapi_app
from app.external.fastapi_app.config import JWTConfig


class Default(WorkerEntrypoint):
    def __init__(self, ctx, env):
        super().__init__(ctx, env)
        LoggerConfig.set_level(self.env.LOGGER_LEVEL)
        JWTConfig.set_secret(self.env.JWT_SECRET)
        self.database = Database({"binding": True, "DB": self.env.DB})
        database_ctx.set(self.database)
        # Create tables if not exist
        DatabaseBaseModel.metadata.create_all(bind=self.database.engine)

    async def fetch(self, request: Request):
        # url = urlparse(request.url)
        # if url.path.startswith("/static"):
        #     return await self.env.ASSETS.fetch(request)

        import asgi

        with self.database.session_local() as session:
            token = db_session.set(session)  # Store session for THIS request only
            try:
                return await asgi.fetch(
                    fastapi_app,
                    request.js_object,
                    self.env,
                )
            finally:
                db_session.reset(token)  # Clean up session after request
