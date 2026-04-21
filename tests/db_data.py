from uuid import uuid4

from app.external.fastapi_app.context import db_session
from app.external.database import database_models as models
from app.external.fastapi_app.auth import hash_password


def generate_user():
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
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user, pwd


def generate_notification(user_id: int) -> models.NotificationModel:
    """Create a test notification

    Returns:
        models.Notification: Returns the notification
    """
    db = db_session.get()
    new_notification = models.NotificationModel(
        user_id=user_id,
        channel_id="email",
        title="Test Notification",
        content="This is the content of the notification",
        recipient="testrecipient@example.com",
    )
    db.add(new_notification)
    db.commit()
    db.refresh(new_notification)
    return new_notification
