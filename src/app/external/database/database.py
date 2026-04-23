from dataclasses import asdict

from app.core.database import IDatabase

from sqlalchemy_cloudflare_d1 import create_engine_from_binding
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, select, func, update, delete

from app.core.user import User
from app.core.notification import Notification
from app.external.database import database_models as models
from ..fastapi_app.context import db_session


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

    async def get_current_session(self):
        """Get the current session set on the beginning of each request.

        Returns:
            Session: SQL database session
        """
        return db_session.get()

    async def create_user(self, user):
        session = await self.get_current_session()
        u = models.UserModel(**asdict(user))
        session.add(u)
        session.commit()
        return User(
            id=u.id,
            email=u.email,
            password_hash=u.password_hash,
            enabled=u.enabled,
            role=u.role,
            created_at=u.created_at,
        )

    async def get_user(self, user_id=None, user_email=None):
        session = await self.get_current_session()
        if user_id:
            result = session.execute(
                select(models.UserModel).where(
                    models.UserModel.id == user_id,
                )
            )
            user = result.scalars().first()
        elif user_email:
            result = session.execute(
                select(models.UserModel).where(
                    func.lower(models.UserModel.email) == user_email.lower(),
                )
            )
            user = result.scalars().first()
        else:
            raise ValueError("ID or email must be provided")
        return (
            User(
                id=user.id,
                email=user.email,
                password_hash=user.password_hash,
                enabled=user.enabled,
                role=user.role,
                created_at=user.created_at,
            )
            if user
            else None
        )

    async def get_all_users(self):
        session = await self.get_current_session()
        result = session.execute(select(models.UserModel))
        r = result.scalars().all()
        return [
            User(
                id=u.id,
                email=u.email,
                password_hash=u.password_hash,
                enabled=u.enabled,
                role=u.role,
                created_at=u.created_at,
            )
            for u in r
        ]

    async def update_user(self, user_id, user):
        session = await self.get_current_session()
        session.execute(
            update(models.UserModel)
            .where(
                models.UserModel.id == user_id,
            )
            .values(**asdict(user))
        )
        session.commit()

    async def delete_user(self, user_id):
        session = await self.get_current_session()
        session.execute(
            delete(models.UserModel).where(
                models.UserModel.id == user_id,
            )
        )
        session.commit()

    async def get_notification(self, notification_id: int):
        session = await self.get_current_session()
        result = session.execute(
            select(models.NotificationModel).where(
                models.NotificationModel.id == notification_id,
            )
        )
        notif = result.scalars().first()
        return (
            Notification(
                id=notif.id,
                user_id=notif.user_id,
                channel_id=notif.channel_id,
                status=notif.status,
                recipient=notif.recipient,
                title=notif.title,
                content=notif.content,
                inserted_at=notif.inserted_at,
            )
            if notif
            else None
        )

    async def get_all_notifications_by_user_id(self, user_id: int):
        session = await self.get_current_session()
        result = session.execute(
            select(models.NotificationModel).where(
                models.NotificationModel.user_id == user_id,
            )
        )
        r = result.scalars().all()
        return [
            Notification(
                id=n.id,
                user_id=n.user_id,
                channel_id=n.channel_id,
                status=n.status,
                recipient=n.recipient,
                title=n.title,
                content=n.content,
                inserted_at=n.inserted_at,
            )
            for n in r
        ]
