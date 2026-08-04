import sys

sys.path.append("./src")

import asyncio
from datetime import UTC, datetime, timedelta

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import delete

from app.core.user import User
from app.core.channel import Channel, ChannelType
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
        "password": "test",
    },
]


CHANNELS = [
    {
        "reference": 1,  # used to link notifications to this channel
        "email": "admin@test.com",  # used to link with user when inserting to db
        "type": ChannelType.EMAIL,
        "credential_user": "someemail@asd.com",
        "credential_pass": "somepassword123",
        "resource_url": "some.smtp.server",
        "port_url": 123,
        "sender_name": "Jorge Admin",
    },
    {
        "reference": 2,
        "email": "test1@test.com",
        "type": ChannelType.EMAIL,
        "credential_user": "test1.email@asd.com",
        "credential_pass": "somepassword123",
        "resource_url": "smtp.test1.server",
        "port_url": 587,
        "sender_name": "Test One Email",
    },
    {
        "reference": 3,
        "email": "test1@test.com",
        "type": ChannelType.SMS,
        "credential_user": "54_9_3400123456",
        "credential_pass": "somepassword123",
        "resource_url": "sms.test1.server",
        "port_url": 9090,
        "sender_name": "Test One SMS",
    },
    {
        "reference": 4,
        "email": "test1@test.com",
        "type": ChannelType.PUSH,
        "credential_user": "test1.push.device",
        "credential_pass": "somepassword123",
        "resource_url": "push.test1.server",
        "port_url": 443,
        "sender_name": "Test One Push",
    },
    {
        "reference": 5,
        "email": "test2@test.com",
        "type": ChannelType.EMAIL,
        "credential_user": "test2.email@asd.com",
        "credential_pass": "somepassword123",
        "resource_url": "smtp.test2.server",
        "port_url": 587,
        "sender_name": "Test Two Email",
    },
    {
        "reference": 6,
        "email": "test2@test.com",
        "type": ChannelType.SMS,
        "credential_user": "54_9_3400123457",
        "credential_pass": "somepassword123",
        "resource_url": "sms.test2.server",
        "port_url": 9090,
        "sender_name": "Test Two SMS",
    },
    {
        "reference": 7,
        "email": "test2@test.com",
        "type": ChannelType.EMAIL,
        "credential_user": "test2.alt@asd.com",
        "credential_pass": "somepassword123",
        "resource_url": "smtp.test2.alt.server",
        "port_url": 465,
        "sender_name": "Test Two Email Alt",
    },
    {
        "reference": 8,
        "email": "test3@test.com",
        "type": ChannelType.EMAIL,
        "credential_user": "test3.email@asd.com",
        "credential_pass": "somepassword123",
        "resource_url": "smtp.test3.server",
        "port_url": 587,
        "sender_name": "Test Three Email",
    },
    {
        "reference": 9,
        "email": "test3@test.com",
        "type": ChannelType.SMS,
        "credential_user": "54_9_3400123458",
        "credential_pass": "somepassword123",
        "resource_url": "sms.test3.server",
        "port_url": 9090,
        "sender_name": "Test Three SMS",
    },
    {
        "reference": 10,
        "email": "test3@test.com",
        "type": ChannelType.PUSH,
        "credential_user": "test3.push.device",
        "credential_pass": "somepassword123",
        "resource_url": "push.test3.server",
        "port_url": 443,
        "sender_name": "Test Three Push",
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
    {
        "c_reference": 1,
        "status": NotifStatus.SUCCESS,
        "recipient": "maria.lopez@example.com",
        "title": "Invoice ready for review",
        "content": "Your February invoice has been generated and is ready for review in the billing portal.",
    },
    {
        "c_reference": 2,
        "status": NotifStatus.SUCCESS,
        "recipient": "alex.pereira@example.com",
        "title": "Weekly digest is available",
        "content": "Your weekly summary is ready. Open the dashboard to see the latest activity and trends.",
    },
    {
        "c_reference": 3,
        "status": NotifStatus.SUCCESS,
        "recipient": "54_9_1133001001",
        "title": "Verification code",
        "content": "Your verification code is 482913. It expires in 10 minutes.",
    },
    {
        "c_reference": 4,
        "status": NotifStatus.SUCCESS,
        "recipient": "device-token-7f4b2c",
        "title": "Backup completed",
        "content": "The latest backup finished successfully and all files were synced.",
    },
    {
        "c_reference": 5,
        "status": NotifStatus.SENT,
        "recipient": "sofia.garcia@example.com",
        "title": "Meeting reminder",
        "content": "Reminder: your strategy meeting starts tomorrow at 09:30 in conference room B.",
    },
    {
        "c_reference": 6,
        "status": NotifStatus.SUCCESS,
        "recipient": "54_9_1133001002",
        "title": "Delivery update",
        "content": "Your package is out for delivery and should arrive before the end of the day.",
    },
    {
        "c_reference": 7,
        "status": NotifStatus.SUCCESS,
        "recipient": "lucas.fernandez@example.com",
        "title": "Subscription renewed",
        "content": "Your subscription was renewed successfully and your access remains active.",
    },
    {
        "c_reference": 8,
        "status": NotifStatus.SUCCESS,
        "recipient": "camila.rojas@example.com",
        "title": "Security alert resolved",
        "content": "A recent login alert was reviewed and no further action is required.",
    },
    {
        "c_reference": 9,
        "status": NotifStatus.SUCCESS,
        "recipient": "54_9_1133001003",
        "title": "Appointment confirmed",
        "content": "Your appointment has been confirmed for Thursday at 16:00.",
    },
    {
        "c_reference": 1,
        "status": NotifStatus.SUCCESS,
        "recipient": "finance.team@example.com",
        "title": "Payment received",
        "content": "We received the payment for your last order and the receipt is attached in the portal.",
    },
    {
        "c_reference": 2,
        "status": NotifStatus.SUCCESS,
        "recipient": "diego.martin@example.com",
        "title": "New comment on your ticket",
        "content": "Support added a new comment to your open ticket. Please review the latest update.",
    },
    {
        "c_reference": 3,
        "status": NotifStatus.SUCCESS,
        "recipient": "54_9_1133001004",
        "title": "One-time password",
        "content": "Use code 715408 to continue signing in. This code is valid for 5 minutes.",
    },
    {
        "c_reference": 5,
        "status": NotifStatus.SUCCESS,
        "recipient": "andrea.silva@example.com",
        "title": "Report exported",
        "content": "Your monthly report export is ready and can now be downloaded from the reports page.",
    },
    {
        "c_reference": 8,
        "status": NotifStatus.ERROR,
        "recipient": "jorge.rolando@example.com",
        "title": "New device connected",
        "content": "A new device signed into your account from a recognized location.",
    },
    {
        "c_reference": 1,
        "status": NotifStatus.SUCCESS,
        "recipient": "billing@example.com",
        "title": "Monthly statement generated",
        "content": "Your monthly statement is ready and can be downloaded from the account portal.",
    },
    {
        "c_reference": 2,
        "status": NotifStatus.SUCCESS,
        "recipient": "olivia.moreno@example.com",
        "title": "Password reset requested",
        "content": "We received a password reset request for your account. If this was not you, ignore this message.",
    },
    {
        "c_reference": 3,
        "status": NotifStatus.SUCCESS,
        "recipient": "54_9_1133001005",
        "title": "Login verification code",
        "content": "Use code 304761 to complete sign in. The code expires in 10 minutes.",
    },
    {
        "c_reference": 4,
        "status": NotifStatus.SUCCESS,
        "recipient": "device-token-44a91f",
        "title": "Sync finished",
        "content": "Your device sync completed successfully and all changes are now up to date.",
    },
    {
        "c_reference": 5,
        "status": NotifStatus.SUCCESS,
        "recipient": "paula.navarro@example.com",
        "title": "Invoice payment confirmed",
        "content": "We confirmed your latest invoice payment and updated your account balance.",
    },
    {
        "c_reference": 6,
        "status": NotifStatus.ERROR,
        "recipient": "54_9_1133001006",
        "title": "Pickup window reminder",
        "content": "Your pickup window starts in one hour. Please be ready with your confirmation number.",
    },
    {
        "c_reference": 7,
        "status": NotifStatus.ERROR,
        "recipient": "marcos.vera@example.com",
        "title": "New document shared",
        "content": "A new document was shared with you and is available in the shared files section.",
    },
    {
        "c_reference": 8,
        "status": NotifStatus.SUCCESS,
        "recipient": "lucia.flores@example.com",
        "title": "Security review passed",
        "content": "Your recent activity review is complete and no suspicious behavior was found.",
    },
    {
        "c_reference": 9,
        "status": NotifStatus.SUCCESS,
        "recipient": "54_9_1133001007",
        "title": "Appointment reminder",
        "content": "This is a reminder for your appointment tomorrow at 11:30.",
    },
    {
        "c_reference": 1,
        "status": NotifStatus.SUCCESS,
        "recipient": "reports@example.com",
        "title": "Quarterly report ready",
        "content": "Your quarterly report has been generated and is ready to review in the reports dashboard.",
    },
    {
        "c_reference": 2,
        "status": NotifStatus.SUCCESS,
        "recipient": "carlos.suarez@example.com",
        "title": "Subscription renewal pending",
        "content": "Your subscription will renew soon. Review your billing settings if you want to make changes.",
    },
    {
        "c_reference": 3,
        "status": NotifStatus.PENDING,
        "recipient": "54_9_1133001008",
        "title": "Delivery confirmation code",
        "content": "Share code 918204 with the courier to confirm the delivery handoff.",
    },
    {
        "c_reference": 5,
        "status": NotifStatus.PENDING,
        "recipient": "agustin.rios@example.com",
        "title": "Task completed",
        "content": "The background task finished successfully and the final results are available now.",
    },
    {
        "c_reference": 8,
        "status": NotifStatus.PENDING,
        "recipient": "security.alerts@example.com",
        "title": "Unusual sign-in detected",
        "content": "We detected a sign-in from a new device and locked the session until you confirm it.",
    },
    {
        "c_reference": 9,
        "status": NotifStatus.SENDING,
        "recipient": "54_9_1133001009",
        "title": "Verification call scheduled",
        "content": "Your verification call is scheduled for later today. Please keep your phone available.",
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
