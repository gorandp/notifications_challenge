from app.core.database import IDatabase

from sqlalchemy_cloudflare_d1 import create_engine_from_binding
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, select

from app.core.user import User
from app.core.notification import Notification
from app.external.database import database_models as models
from ..fastapi_app.context import get_session


class Database(IDatabase):
    def __init__(self, connection_params):
        if connection_params.get("binding") is True:
            self._d1 = connection_params.get("DB")
            self.engine = create_engine_from_binding(self._d1)
        else:
            # Mainly for testing
            self._d1 = None
            self.engine = create_engine(
                connection_params.get("url"),
                connect_args={"check_same_thread": False},
            )
        self.session_local = sessionmaker(bind=self.engine)

    async def get_user(self, user_id):
        db = await get_session()
        result = db.execute(
            select(models.UserModel).where(
                models.UserModel.id == user_id,
            )
        )
        user = result.scalars().first()
        return User(**user) if user else None

    async def get_all_users(self):
        db = await get_session()
        result = db.execute(select(models.UserModel))
        r = result.scalars().all()
        return [User(**u) for u in r]

    async def get_notification(self, notification_id: int):
        db = await get_session()
        result = db.execute(
            select(models.NotificationModel).where(
                models.NotificationModel.id == notification_id,
            )
        )
        notif = result.scalars().first()
        return Notification(**notif) if notif else None

    async def get_all_notifications_by_user_id(self, user_id: int):
        db = await get_session()
        result = db.execute(
            select(models.NotificationModel).where(
                models.NotificationModel.user_id == user_id,
            )
        )
        r = result.scalars().all()
        return [Notification(**n) for n in r]
