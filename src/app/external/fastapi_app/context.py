from contextvars import ContextVar
from sqlalchemy.orm import Session

from app.core.database import IDatabase
from app.core.user_repository import IUserRepository
from app.core.user_service import IUserService

from app.interface.user_repository import UserRepository
from app.interface.user_service import UserService

# ContextVar to handle session context safely
database_ctx: ContextVar[IDatabase] = ContextVar("database")
db_session: ContextVar[Session] = ContextVar("db_session")

user_repository_ctx: ContextVar[IUserRepository] = ContextVar("user_repository")
user_service_ctx: ContextVar[IUserService] = ContextVar("user_service")


def init_context(db: IDatabase):
    database_ctx.set(db)

    u_repo = UserRepository(db)
    user_repository_ctx.set(u_repo)

    u_service = UserService(u_repo)
    user_service_ctx.set(u_service)


async def get_session() -> Session:
    return db_session.get()


async def get_db() -> IDatabase:
    return database_ctx.get()
