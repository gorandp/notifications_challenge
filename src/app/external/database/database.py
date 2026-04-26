from dataclasses import asdict

from app.core.database import IDatabase

from sqlalchemy_cloudflare_d1 import create_engine_from_binding
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, select, func, update, delete

from app.core.user import User
from app.core.notification import Notification
from app.core.channel import Channel
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
                channel_type=notif.channel_type,
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
                channel_type=n.channel_type,
                status=n.status,
                recipient=n.recipient,
                title=n.title,
                content=n.content,
                inserted_at=n.inserted_at,
            )
            for n in r
        ]

    async def create_channel(self, channel):
        session = await self.get_current_session()
        c = models.ChannelModel(**asdict(channel))
        session.add(c)
        session.commit()
        return Channel(
            id=c.id,
            user_id=c.user_id,
            type=c.type,
            credential_user=c.credential_user,
            credential_pass=c.credential_pass,
            resource_url=c.resource_url,
            port_url=c.port_url,
        )

    async def get_channel(self, channel_id=None, user_id=None, channel_type=None):
        session = await self.get_current_session()
        if channel_id is not None:
            r = session.execute(
                select(models.ChannelModel)
                .where(models.ChannelModel.id == channel_id)
                .limit(1)
            )
            c = r.scalars().first()
        else:
            r = session.execute(
                select(models.ChannelModel)
                .where(
                    models.ChannelModel.user_id == user_id,
                    models.ChannelModel.type == channel_type,
                )
                .limit(1)
            )
            c = r.scalars().first()
        return Channel(
            id=c.id,
            user_id=c.user_id,
            type=c.type,
            credential_user=c.credential_user,
            credential_pass=c.credential_pass,
            resource_url=c.resource_url,
            port_url=c.port_url,
        )

    async def get_all_channels(self, user_id=None):
        session = await self.get_current_session()
        if not user_id:
            r = session.execute(select(models.ChannelModel))
            cs = r.scalars().all()
        else:
            r = session.execute(
                select(models.ChannelModel).where(
                    models.ChannelModel.user_id == user_id,
                )
            )
            cs = r.scalars().all()
        return [
            Channel(
                id=c.id,
                user_id=c.user_id,
                type=c.type,
                credential_user=c.credential_user,
                credential_pass=c.credential_pass,
                resource_url=c.resource_url,
                port_url=c.port_url,
            )
            for c in cs
        ]

    async def update_channel(self, channel_id, channel):
        session = await self.get_current_session()
        session.execute(
            update(models.ChannelModel)
            .where(
                models.ChannelModel.id == channel_id,
            )
            .values(**asdict(channel))
        )
        session.commit()

    async def delete_channel(self, channel_id):
        session = await self.get_current_session()
        session.execute(
            delete(models.ChannelModel).where(
                models.ChannelModel.id == channel_id,
            )
        )
        session.commit()
