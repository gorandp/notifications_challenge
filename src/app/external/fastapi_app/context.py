from contextvars import ContextVar
from sqlalchemy.orm import Session

from app.core.database import IDatabase

# ContextVar to handle session context safely
database_ctx: ContextVar[IDatabase] = ContextVar("database")
db_session: ContextVar[Session] = ContextVar("db_session")


async def get_session() -> Session:
    return db_session.get()


async def get_db() -> IDatabase:
    return database_ctx.get()
