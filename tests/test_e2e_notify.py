# After creation, the notification will be sent via the selected channel
# Channels: Email, SMS, Push notification, Telegram
# Each channel requires a different sending logic
from fastapi import status

from app.core.notification import NotifStatus
from db_data import (
    generate_user,
    generate_notification,
    generate_an_email_channel,
)
from auth import login


def create_notification_and_send(client):
    user, pwd = generate_user()
    channel = generate_an_email_channel(user.id)
    JSON_BODY = {
        "channel_id": channel.id,
        "title": "Test Notification",
        "content": "Test Content",
        "recipient": "recipient@example.com",
        "send_after_creating": True,
    }

    token = login(client, user.email, pwd)

    # Create notification
    r = client.post(
        "/notifications",
        headers={"Authorization": f"Bearer {token}"},
        json=JSON_BODY,
    )
    assert r.status_code == status.HTTP_201_CREATED
    data_create = r.json()
    assert "id" in data_create
    new_notif_id = data_create["id"]

    # Check created
    r = client.get(
        "/notifications",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == status.HTTP_200_OK
    data_after = r.json()
    assert isinstance(data_after, list)
    assert len(data_after) == 1
    assert data_after[0]["id"] == new_notif_id
    assert data_after[0]["status"] == NotifStatus.SENT.value
    assert "sent_at" in data_after[0]


def send_already_created_notification(client):
    user, pwd = generate_user()
    channel = generate_an_email_channel(user.id)
    notification = generate_notification(user.id, channel.id, channel.type)

    token = login(client, user.email, pwd)

    # Check status
    r = client.get(
        f"/notifications/{notification.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == status.HTTP_200_OK
    data_before = r.json()
    assert data_before["status"] == NotifStatus.PENDING.value
    assert data_before.get("sent_at") is None

    r = client.post(
        f"/notifications/{notification.id}/send",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == status.HTTP_200_OK

    # Check after send
    r = client.get(
        f"/notifications/{notification.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == status.HTTP_200_OK
    data_after = r.json()
    assert data_after["status"] == NotifStatus.SENT.value
    assert data_after.get("sent_at") is not None
