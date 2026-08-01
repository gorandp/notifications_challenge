# Create
# Edit
# Delete
# Query all
import pytest
from fastapi import status

from app.core.notification import NotifStatus
from tests.db_data import (
    generate_user,
    generate_notification,
    generate_an_email_channel,
)
from tests.auth import login


# ------------------ #
# ----- CREATE ----- #
# ------------------ #


@pytest.mark.anyio
async def test_create_notification(client):
    user, pwd = await generate_user()
    channel = await generate_an_email_channel(user.id)
    JSON_BODY = {
        "channel_id": channel.id,
        "status": NotifStatus.PENDING.value,
        "title": "Test Notification",
        "content": "Test Content",
        "recipient": "recipient@example.com",
        "send_after_creating": False,
    }

    r = await client.post("/notifications", json=JSON_BODY)
    assert r.status_code == status.HTTP_401_UNAUTHORIZED

    token = await login(client, user.email, pwd)

    # Check unchanged
    r = await client.get(
        "/notifications",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == status.HTTP_200_OK
    data_before = r.json()
    assert isinstance(data_before, list)
    assert len(data_before) == 0

    # Create notification
    r = await client.post(
        "/notifications",
        headers={"Authorization": f"Bearer {token}"},
        json=JSON_BODY,
    )
    assert r.status_code == status.HTTP_201_CREATED
    data_create = r.json()
    assert "id" in data_create
    new_notif_id = data_create["id"]

    # Check created
    r = await client.get(
        "/notifications",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == status.HTTP_200_OK
    data_after = r.json()
    assert isinstance(data_after, list)
    assert len(data_after) == 1
    assert data_after[0]["id"] == new_notif_id


# ------------------ #
# ------ READ ------ #
# ------------------ #


@pytest.mark.anyio
async def test_auth_get_notifications(client):
    user, pwd = await generate_user()

    # Unauthenticated
    r = await client.get("/notifications")
    assert r.status_code == status.HTTP_401_UNAUTHORIZED

    token = await login(client, user.email, pwd)

    # Authenticated
    r = await client.get(
        "/notifications",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    assert isinstance(data, list)
    assert len(data) == 0
    assert r.json() == []


@pytest.mark.anyio
async def test_get_notifications(client):
    user, pwd = await generate_user()
    channel = await generate_an_email_channel(user.id)
    notification = await generate_notification(
        user.id,
        channel.id,
        channel.type,
    )
    token = await login(client, user.email, pwd)

    r = await client.get(
        "/notifications",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    assert data[0]["id"] == notification.id


@pytest.mark.anyio
async def test_get_notification(client):
    user, pwd = await generate_user()
    channel = await generate_an_email_channel(user.id)
    notification = await generate_notification(
        user.id,
        channel.id,
        channel.type,
    )
    token = await login(client, user.email, pwd)

    r = await client.get(
        f"/notifications/{notification.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    assert data["id"] == notification.id

    r = await client.get(
        "/notifications/9999",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.anyio
async def test_get_notifications_ownership(client):
    u1, pwd1 = await generate_user()
    u2, pwd2 = await generate_user()
    channel1 = await generate_an_email_channel(u1.id)
    notification1 = await generate_notification(
        u1.id,
        channel1.id,
        channel1.type,
    )
    channel2 = await generate_an_email_channel(u2.id)
    notification2 = await generate_notification(
        u2.id,
        channel2.id,
        channel2.type,
    )

    token1 = await login(client, u1.email, pwd1)

    r = await client.get(
        "/notifications",
        headers={"Authorization": f"Bearer {token1}"},
    )
    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    assert len(data) == 1
    assert data[0]["id"] == notification1.id

    token2 = await login(client, u2.email, pwd2)

    r = await client.get(
        "/notifications",
        headers={"Authorization": f"Bearer {token2}"},
    )
    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    assert len(data) == 1
    assert data[0]["id"] == notification2.id


@pytest.mark.anyio
async def test_get_notification_ownership(client):
    u1, pwd1 = await generate_user()
    u2, pwd2 = await generate_user()
    channel = await generate_an_email_channel(u1.id)
    # Notification owned by User 1
    notification = await generate_notification(
        u1.id,
        channel.id,
        channel.type,
    )

    # User 2 login
    token2 = await login(client, u2.email, pwd2)

    r = await client.get(
        f"/notifications/{notification.id}",
        headers={"Authorization": f"Bearer {token2}"},
    )
    assert r.status_code == status.HTTP_404_NOT_FOUND

    # User 1 login
    token1 = await login(client, u1.email, pwd1)

    r = await client.get(
        f"/notifications/{notification.id}",
        headers={"Authorization": f"Bearer {token1}"},
    )
    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    assert data["id"] == notification.id


@pytest.mark.anyio
async def test_get_notification_admin(client):
    u1, pwd1 = await generate_user()
    u_admin, pwd_admin = await generate_user("admin")
    channel = await generate_an_email_channel(u1.id)
    # Notification owned by User 1
    notification = await generate_notification(
        u1.id,
        channel.id,
        channel.type,
    )

    # Admin user
    token_admin = await login(client, u_admin.email, pwd_admin)

    r = await client.get(
        f"/notifications/{notification.id}",
        headers={"Authorization": f"Bearer {token_admin}"},
    )
    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    assert data["id"] == notification.id

    # User 1
    token1 = await login(client, u1.email, pwd1)

    r = await client.get(
        f"/notifications/{notification.id}",
        headers={"Authorization": f"Bearer {token1}"},
    )
    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    assert data["id"] == notification.id


# ------------------ #
# ----- UPDATE ----- #
# ------------------ #


@pytest.mark.anyio
async def test_update_notification(client):
    user, pwd = await generate_user()
    channel = await generate_an_email_channel(user.id)
    notification = await generate_notification(
        user.id,
        channel.id,
        channel.type,
    )
    EDIT_JSON = {
        "title": "My new title",
        "content": "Modified content",
    }
    assert notification.title != EDIT_JSON["title"]
    assert notification.content != EDIT_JSON["content"]

    # Not authenticated
    r = await client.patch(
        f"/notifications/{notification.id}",
        json=EDIT_JSON,
    )
    assert r.status_code == status.HTTP_401_UNAUTHORIZED

    token = await login(client, user.email, pwd)

    # Check unchanged
    r = await client.get(
        f"/notifications/{notification.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == status.HTTP_200_OK
    data_before = r.json()
    assert data_before["id"] == notification.id
    assert data_before["title"] == notification.title
    assert data_before["content"] == notification.content

    # Update
    r = await client.patch(
        f"/notifications/{notification.id}",
        headers={"Authorization": f"Bearer {token}"},
        json=EDIT_JSON,
    )
    assert r.status_code == status.HTTP_200_OK
    data_update = r.json()
    assert data_update["id"] == notification.id

    # Check updated
    r = await client.get(
        f"/notifications/{notification.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == status.HTTP_200_OK
    data_after = r.json()
    assert data_after["id"] == notification.id
    assert data_after["title"] == EDIT_JSON["title"]
    assert data_after["content"] == EDIT_JSON["content"]


@pytest.mark.anyio
async def test_update_notification_ownership(client):
    u1, pwd1 = await generate_user()
    u2, pwd2 = await generate_user()
    channel = await generate_an_email_channel(u1.id)
    # Notification owned by User 1
    notification = await generate_notification(
        u1.id,
        channel.id,
        channel.type,
    )
    EDIT_JSON_NOT_AUTHORIZED = {
        "title": "My new title from another account",
        "content": "Modified content from another account",
    }
    assert notification.title != EDIT_JSON_NOT_AUTHORIZED["title"]
    assert notification.content != EDIT_JSON_NOT_AUTHORIZED["content"]
    EDIT_JSON_AUTHORIZED = {
        "title": "My new title from the authorized account",
        "content": "Modified content from the authorized account",
    }
    assert notification.title != EDIT_JSON_AUTHORIZED["title"]
    assert notification.content != EDIT_JSON_AUTHORIZED["content"]

    token2 = await login(client, u2.email, pwd2)

    r = await client.patch(
        f"/notifications/{notification.id}",
        headers={"Authorization": f"Bearer {token2}"},
        json=EDIT_JSON_NOT_AUTHORIZED,
    )
    assert r.status_code == status.HTTP_404_NOT_FOUND

    token1 = await login(client, u1.email, pwd1)

    # Check unchanged
    r = await client.get(
        f"/notifications/{notification.id}",
        headers={"Authorization": f"Bearer {token1}"},
    )
    assert r.status_code == status.HTTP_200_OK
    data_before = r.json()
    assert data_before["id"] == notification.id
    assert data_before["title"] == notification.title
    assert data_before["content"] == notification.content

    # Update
    r = await client.patch(
        f"/notifications/{notification.id}",
        headers={"Authorization": f"Bearer {token1}"},
        json=EDIT_JSON_AUTHORIZED,
    )
    assert r.status_code == status.HTTP_200_OK
    data_update = r.json()
    assert data_update["id"] == notification.id

    # Check updated
    r = await client.get(
        f"/notifications/{notification.id}",
        headers={"Authorization": f"Bearer {token1}"},
    )
    assert r.status_code == status.HTTP_200_OK
    data_after = r.json()
    assert data_after["id"] == notification.id
    assert data_after["title"] == EDIT_JSON_AUTHORIZED["title"]
    assert data_after["content"] == EDIT_JSON_AUTHORIZED["content"]


@pytest.mark.anyio
async def test_update_notification_admin(client):
    u1, pwd1 = await generate_user()
    u_admin, pwd_admin = await generate_user("admin")
    channel = await generate_an_email_channel(u1.id)
    # Notification owned by User 1
    notification = await generate_notification(
        u1.id,
        channel.id,
        channel.type,
    )
    EDIT_JSON_AUTHORIZED = {
        "title": "My new title from the authorized account",
        "content": "Modified content from the authorized account",
    }
    assert notification.title != EDIT_JSON_AUTHORIZED["title"]
    assert notification.content != EDIT_JSON_AUTHORIZED["content"]

    token_admin = await login(client, u_admin.email, pwd_admin)

    # Update
    r = await client.patch(
        f"/notifications/{notification.id}",
        headers={"Authorization": f"Bearer {token_admin}"},
        json=EDIT_JSON_AUTHORIZED,
    )
    assert r.status_code == status.HTTP_200_OK
    data_update = r.json()
    assert data_update["id"] == notification.id

    token1 = await login(client, u1.email, pwd1)

    # Check updated
    r = await client.get(
        f"/notifications/{notification.id}",
        headers={"Authorization": f"Bearer {token1}"},
    )
    assert r.status_code == status.HTTP_200_OK
    data_after = r.json()
    assert data_after["id"] == notification.id
    assert data_after["title"] == EDIT_JSON_AUTHORIZED["title"]
    assert data_after["content"] == EDIT_JSON_AUTHORIZED["content"]


# ------------------ #
# ----- DELETE ----- #
# ------------------ #


@pytest.mark.anyio
async def test_delete_notification(client):
    user, pwd = await generate_user()
    channel = await generate_an_email_channel(user.id)
    notification = await generate_notification(
        user.id,
        channel.id,
        channel.type,
    )

    # Not authenticated
    r = await client.delete(
        f"/notifications/{notification.id}",
    )
    assert r.status_code == status.HTTP_401_UNAUTHORIZED

    token = await login(client, user.email, pwd)

    # Check unchanged
    r = await client.get(
        f"/notifications/{notification.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == status.HTTP_200_OK
    data_before = r.json()
    assert data_before["id"] == notification.id
    assert data_before["title"] == notification.title
    assert data_before["content"] == notification.content

    # Delete
    r = await client.delete(
        f"/notifications/{notification.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == status.HTTP_204_NO_CONTENT

    # Check deleted
    r = await client.get(
        f"/notifications/{notification.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.anyio
async def test_delete_notification_ownership(client):
    u1, pwd1 = await generate_user()
    u2, pwd2 = await generate_user()
    channel = await generate_an_email_channel(u1.id)
    # Notification owned by User 1
    notification = await generate_notification(
        u1.id,
        channel.id,
        channel.type,
    )

    # User 2 login
    token2 = await login(client, u2.email, pwd2)

    # Try delete
    r = await client.delete(
        f"/notifications/{notification.id}",
        headers={"Authorization": f"Bearer {token2}"},
    )
    assert r.status_code == status.HTTP_404_NOT_FOUND

    token1 = await login(client, u1.email, pwd1)

    # Check unchanged
    r = await client.get(
        f"/notifications/{notification.id}",
        headers={"Authorization": f"Bearer {token1}"},
    )
    assert r.status_code == status.HTTP_200_OK
    data_before = r.json()
    assert data_before["id"] == notification.id
    assert data_before["title"] == notification.title
    assert data_before["content"] == notification.content

    # Delete
    r = await client.delete(
        f"/notifications/{notification.id}",
        headers={"Authorization": f"Bearer {token1}"},
    )
    assert r.status_code == status.HTTP_204_NO_CONTENT

    # Check deleted
    r = await client.get(
        f"/notifications/{notification.id}",
        headers={"Authorization": f"Bearer {token1}"},
    )
    assert r.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.anyio
async def test_delete_notification_admin(client):
    u1, pwd1 = await generate_user()
    u_admin, pwd_admin = await generate_user("admin")
    channel = await generate_an_email_channel(u1.id)
    # Notification owned by User 1
    notification = await generate_notification(
        u1.id,
        channel.id,
        channel.type,
    )

    token_admin = await login(client, u_admin.email, pwd_admin)

    # Delete
    r = await client.delete(
        f"/notifications/{notification.id}",
        headers={"Authorization": f"Bearer {token_admin}"},
    )
    assert r.status_code == status.HTTP_204_NO_CONTENT

    token1 = await login(client, u1.email, pwd1)

    # Check deleted
    r = await client.get(
        f"/notifications/{notification.id}",
        headers={"Authorization": f"Bearer {token1}"},
    )
    assert r.status_code == status.HTTP_404_NOT_FOUND
