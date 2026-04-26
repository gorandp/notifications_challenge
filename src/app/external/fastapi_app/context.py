from contextvars import ContextVar
from sqlalchemy.orm import Session

from app.core.database import IDatabase
from app.interface.user_repository import UserRepository
from app.interface.user_service import UserService
from app.interface.channel_repository import ChannelRepository
from app.interface.channel_service import ChannelService
from app.interface.notification_repository import NotificationRepository
from app.interface.notification_service import NotificationService


# ContextVar to handle session context safely
database_ctx: ContextVar[IDatabase] = ContextVar("database")
db_session: ContextVar[Session] = ContextVar("db_session")

user_repository_ctx: ContextVar[UserRepository] = ContextVar("user_repository")
user_service_ctx: ContextVar[UserService] = ContextVar("user_service")
channel_repository_ctx: ContextVar[ChannelRepository] = ContextVar("channel_repository")
channel_service_ctx: ContextVar[ChannelService] = ContextVar("channel_service")
notification_repository_ctx: ContextVar[NotificationRepository] = ContextVar(
    "notification_repository"
)
notification_service_ctx: ContextVar[NotificationService] = ContextVar(
    "notification_service"
)


def init_context(db: IDatabase):
    database_ctx.set(db)

    u_repo = UserRepository(db)
    user_repository_ctx.set(u_repo)

    u_serv = UserService(u_repo)
    user_service_ctx.set(u_serv)

    c_repo = ChannelRepository(db)
    channel_repository_ctx.set(c_repo)

    c_serv = ChannelService(c_repo)
    channel_service_ctx.set(c_serv)

    n_repo = NotificationRepository(db)
    notification_repository_ctx.set(n_repo)

    n_serv = NotificationService(db)
    notification_service_ctx.set(n_serv)


async def get_session() -> Session:
    return db_session.get()


async def get_db() -> IDatabase:
    return database_ctx.get()


async def get_user_service():
    return user_service_ctx.get()


async def get_channel_service():
    return channel_service_ctx.get()


async def get_notification_service():
    return notification_service_ctx.get()
