import sys

sys.path.append("./src")

import asyncio
from datetime import UTC, datetime, timedelta

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import delete

from app.core.user import User
from app.core.channel import Channel
from app.core.notification import Notification, NotifStatus
from app.external.fastapi_app.context import (
    database_ctx,
    db_session,
    user_repository_ctx,
    channel_repository_ctx,
    notification_repository_ctx,
    init_context,
)
from app.external.database import database_models, database
from app.external.fastapi_app.auth import hash_password


class Settings(BaseSettings):
    DB_CONNECTION_STRING: str = (
        "postgresql+psycopg://notifuser:notifpass@localhost:5432/notifdb"
    )

    # Tell Pydantic to read from a .env file
    model_config = SettingsConfigDict(env_file=".env")


env_settings = Settings()
db = database.Database({"url": env_settings.DB_CONNECTION_STRING})
init_context(db)
now = datetime.now(UTC)


USERS = [
    {
        "email": "admin@test.com",
        "password": "test",
        "role": "admin",
    },
    {
        "email": "test1@test.com",
        "password": "test",
    },
    {
        "email": "test2@test.com",
        "password": "test",
    },
    {
        "email": "test3@test.com",
        "password": "test3",
    },
]


CHANNELS = [
    {
        "reference": 1,  # used to link notifications to this channel
        "email": "admin@test.com",  # used to link with user when inserting to db
        "type": "email",
        "credential_user": "someemail@asd.com",
        "credential_pass": "somepassword123",
        "resource_url": "some.smtp.server",
        "port_url": 123,
        "sender_name": "Jorge Admin",
    },
]


NOTIFICATIONS = [
    {
        "c_reference": 1,
        "status": NotifStatus.SUCCESS,
        "recipient": "some.recipient@dfg.com",
        "title": "Running event on wednesday",
        "content": "Hi! I'm contacting you to let you know that this wednesday I'm attending the running event and there is a promotion of a 50% discount with my code \"admin\". Go to myrunningevent.com, see you there!",
    },
]


# Date generation
current = now - timedelta(days=len(NOTIFICATIONS) + 20)
for i, c in enumerate(CHANNELS):
    c["inserted_at"] = current
    c["updated_at"] = current
    if (i + 1) % 10 == 0:
        c["updated_at"] = min(current + timedelta(days=15), now)


current = now - timedelta(days=len(NOTIFICATIONS) + 2)
for i, n in enumerate(NOTIFICATIONS):
    n["inserted_at"] = current
    n["updated_at"] = current
    n["sent_at"] = current + timedelta(seconds=5)
    if (i + 1) % 55 == 0:
        d = min(current + timedelta(days=5), now)
        n["updated_at"] = d
        n["sent_at"] = d


async def clear_existing_data() -> None:
    # Clear database tables (order respects foreign keys)
    print("Clearing existing data")
    session = db_session.get()
    await session.execute(delete(database_models.NotificationModel))
    await session.execute(delete(database_models.ChannelModel))
    await session.execute(delete(database_models.UserModel))
    await session.commit()


async def populate() -> None:
    await clear_existing_data()

    print(f"Creating {len(USERS)} users")
    u_repo = user_repository_ctx.get()
    u_map_id_email = {}
    for user_data in USERS:
        u_data_updated = await u_repo.create_user(
            User(
                email=user_data["email"],
                password_hash=hash_password(user_data["password"]),
                enabled=True,
                role=user_data.get("role") or "basic",
            )
        )
        u_map_id_email[u_data_updated.email] = u_data_updated.id

    print(f"Creating {len(CHANNELS)} channels")
    c_repo = channel_repository_ctx.get()
    c_map_reference_to_c_db: dict[str, Channel] = {}
    for channel_data in CHANNELS:
        c_data_updated = await c_repo.add(
            Channel(
                user_id=u_map_id_email[channel_data["email"]],
                type=channel_data["type"],
                credential_user=channel_data["credential_user"],
                credential_pass=channel_data["credential_pass"],
                resource_url=channel_data["resource_url"],
                port_url=channel_data["port_url"],
                sender_name=channel_data.get("sender_name"),
                inserted_at=channel_data.get("inserted_at"),
                updated_at=channel_data.get("updated_at"),
            )
        )
        c_map_reference_to_c_db[channel_data["reference"]] = c_data_updated

    print(f"Creating {len(NOTIFICATIONS)} notifications")
    n_repo = notification_repository_ctx.get()
    for notif_data in NOTIFICATIONS:
        c = c_map_reference_to_c_db[notif_data["c_reference"]]
        await n_repo.add(
            Notification(
                user_id=c.user_id,
                channel_id=c.id,
                channel_type=c.type,
                status=notif_data["status"],
                recipient=notif_data["recipient"],
                title=notif_data["title"],
                content=notif_data["content"],
                inserted_at=notif_data["inserted_at"],
                updated_at=notif_data["updated_at"],
                sent_at=notif_data.get("sent_at"),
            )
        )

    print("Done!")


async def main():
    db: database.Database = database_ctx.get()
    async with db.async_session_local() as session:
        token = db_session.set(session)
        await populate()
        db_session.reset(token)
    await db.engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
