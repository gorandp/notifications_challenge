from dataclasses import asdict

from sqlalchemy_cloudflare_d1 import create_engine_from_binding
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, select, func, update, delete

from app.core.database import IDatabase
from app.external.database import database_models as models
from app.external.database import database_mappers as mappers
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
        u = mappers.dump_user_to_db_model(user)
        session.add(u)
        session.commit()
        return mappers.load_user_from_db_model(u)

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
        return mappers.load_user_from_db_model(user)

    async def get_all_users(self):
        session = await self.get_current_session()
        result = session.execute(select(models.UserModel))
        r = result.scalars().all()
        return [mappers.load_user_from_db_model(u) for u in r]

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

    async def create_notification(self, notification):
        session = await self.get_current_session()
        n = mappers.dump_notification_to_db_model(notification)
        session.add(n)
        session.commit()
        return mappers.load_notification_from_db_model(n)

    async def get_notification(self, notification_id: int):
        session = await self.get_current_session()
        result = session.execute(
            select(models.NotificationModel).where(
                models.NotificationModel.id == notification_id,
            )
        )
        notif = result.scalars().first()
        return mappers.load_notification_from_db_model(notif)

    async def get_all_notifications_by_user_id(self, user_id: int):
        session = await self.get_current_session()
        result = session.execute(
            select(models.NotificationModel).where(
                models.NotificationModel.user_id == user_id,
            )
        )
        r = result.scalars().all()
        return [mappers.load_notification_from_db_model(n) for n in r]

    async def update_notification(self, notification_id, notification):
        session = await self.get_current_session()
        session.execute(
            update(models.NotificationModel)
            .where(models.NotificationModel.id == notification_id)
            .values(**asdict(notification))
        )
        session.commit()

    async def delete_notification(self, notification_id):
        session = await self.get_current_session()
        session.execute(
            delete(models.NotificationModel).where(
                models.NotificationModel.id == notification_id,
            )
        )
        session.commit()

    async def create_channel(self, channel):
        session = await self.get_current_session()
        c = mappers.dump_channel_to_db_model(channel)
        session.add(c)
        session.commit()
        return mappers.load_channel_from_db_model(c)

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
        return mappers.load_channel_from_db_model(c)

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
        return [mappers.load_channel_from_db_model(c) for c in cs]

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
