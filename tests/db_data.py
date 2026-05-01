from uuid import uuid4

from app.core.notification import NotifStatus
from app.external.fastapi_app.context import db_session
from app.external.database import database_models as models
from app.external.fastapi_app.auth import hash_password
from app.interface.channel_strategies.email_mock_server import SMTP_DEBUG_SERVER


def generate_user(role="basic"):
    """Create a test user

    Returns:
        tuple[models.User, str]: Returns the user and original password
    """
    db = db_session.get()
    pwd = str(uuid4())
    password_hash = hash_password(pwd)
    new_user = models.UserModel(
        email=f"{uuid4()}@example.com",
        password_hash=password_hash,
        enabled=True,
        role=role,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user, pwd


def generate_an_email_channel(user_id: int) -> models.ChannelModel:
    """Create a test email channel

    Args:
        user_id (int): User ID

    Returns:
        models.ChannelModel: Returns the channel
    """
    db = db_session.get()
    new_channel = models.ChannelModel(
        user_id=user_id,
        type="email",
        credential_user="username",
        credential_pass="userpassword",
        resource_url=SMTP_DEBUG_SERVER,
        port_url=587,
    )
    db.add(new_channel)
    db.commit()
    db.refresh(new_channel)
    return new_channel


def generate_a_sms_channel(user_id: int) -> models.ChannelModel:
    """Create a test SMS channel

    Args:
        user_id (int): User ID

    Returns:
        models.ChannelModel: Returns the channel
    """
    db = db_session.get()
    new_channel = models.ChannelModel(
        user_id=user_id,
        type="sms",
        credential_user="username",
        credential_pass="userpassword",
        resource_url="sms.service.com",  # not real
        port_url=999,  # not real
    )
    db.add(new_channel)
    db.commit()
    db.refresh(new_channel)
    return new_channel


def generate_notification(
    user_id: int,
    channel_id: int,
    channel_type: str,
) -> models.NotificationModel:
    """Create a test notification

    Returns:
        models.Notification: Returns the notification
    """
    db = db_session.get()
    new_notification = models.NotificationModel(
        user_id=user_id,
        channel_id=channel_id,
        channel_type=channel_type,
        status=NotifStatus.PENDING.value,
        title="Test Notification",
        content="This is the content of the notification",
        recipient="testrecipient@example.com",
    )
    db.add(new_notification)
    db.commit()
    db.refresh(new_notification)
    return new_notification
