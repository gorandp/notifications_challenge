from dataclasses import asdict

from app.core.user import User
from app.core.channel import Channel
from app.core.notification import Notification
from app.external.database.database_models import (
    UserModel,
    ChannelModel,
    NotificationModel,
)


def dump_user_to_db_model(u: User):
    return UserModel(**asdict(u))


def load_user_from_db_model(u: UserModel | None):
    if u is None:
        return None
    return User(
        id=u.id,
        email=u.email,
        password_hash=u.password_hash,
        enabled=u.enabled,
        role=u.role,
        created_at=u.created_at,
    )


def dump_channel_to_db_model(c: Channel):
    return ChannelModel(**asdict(c))


def load_channel_from_db_model(c: ChannelModel | None):
    if c is None:
        return None
    return Channel(
        id=c.id,
        user_id=c.user_id,
        type=c.type,
        credential_user=c.credential_user,
        credential_pass=c.credential_pass,
        resource_url=c.resource_url,
        port_url=c.port_url,
    )


def dump_notification_to_db_model(n: Notification):
    return NotificationModel(**asdict(n))


def load_notification_from_db_model(n: NotificationModel | None):
    if n is None:
        return None
    return Notification(
        id=n.id,
        user_id=n.user_id,
        channel_id=n.channel_id,
        channel_type=n.channel_type,
        status=n.status,
        recipient=n.recipient,
        title=n.title,
        content=n.content,
        inserted_at=n.inserted_at,
        updated_at=n.updated_at,
        sent_at=n.sent_at,
    )
