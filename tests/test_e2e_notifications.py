# Create
# Edit
# Delete
# Query all
from fastapi import status

from app.core.notification import NotifStatus
from db_data import (
    generate_user,
    generate_notification,
    generate_an_email_channel,
)
from auth import login


def test_create_notification(client):
    user, pwd = generate_user()
    channel = generate_an_email_channel(user.id)
    JSON_BODY = {
        "channel_id": channel.id,
        "status": NotifStatus.PENDING.value,
        "title": "Test Notification",
        "content": "Test Content",
        "recipient": "recipient@example.com",
    }

    r = client.post("/notifications", json=JSON_BODY)
    assert r.status_code == status.HTTP_401_UNAUTHORIZED

    token = login(client, user.email, pwd)

    # Check unchanged
    r = client.get(
        "/notifications",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == status.HTTP_200_OK
    data_before = r.json()
    assert isinstance(data_before, list)
    assert len(data_before) == 0

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


def test_auth_get_notifications(client):
    user, pwd = generate_user()

    # Unauthenticated
    r = client.get("/notifications")
    assert r.status_code == status.HTTP_401_UNAUTHORIZED

    token = login(client, user.email, pwd)

    # Authenticated
    r = client.get(
        "/notifications",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    assert isinstance(data, list)
    assert len(data) == 0
    assert r.json() == []


def test_get_notifications(client):
    user, pwd = generate_user()
    channel = generate_an_email_channel(user.id)
    notification = generate_notification(
        user.id,
        channel.id,
        channel.type,
    )
    token = login(client, user.email, pwd)

    r = client.get(
        "/notifications",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    assert data[0]["id"] == notification.id


def test_get_notification(client):
    user, pwd = generate_user()
    channel = generate_an_email_channel(user.id)
    notification = generate_notification(
        user.id,
        channel.id,
        channel.type,
    )
    token = login(client, user.email, pwd)

    r = client.get(
        f"/notifications/{notification.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    assert data["id"] == notification.id


def test_get_notifications_ownership(client):
    u1, pwd1 = generate_user()
    u2, pwd2 = generate_user()
    channel1 = generate_an_email_channel(u1.id)
    notification1 = generate_notification(
        u1.id,
        channel1.id,
        channel1.type,
    )
    channel2 = generate_an_email_channel(u1.id)
    notification2 = generate_notification(
        u2.id,
        channel2.id,
        channel2.type,
    )

    token1 = login(client, u1.email, pwd1)

    r = client.get(
        "/notifications",
        headers={"Authorization": f"Bearer {token1}"},
    )
    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    assert len(data) == 1
    assert data[0]["id"] == notification1.id

    token2 = login(client, u2.email, pwd2)

    r = client.get(
        "/notifications",
        headers={"Authorization": f"Bearer {token2}"},
    )
    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    assert len(data) == 1
    assert data[0]["id"] == notification2.id


def test_get_notification_ownership(client):
    u1, pwd1 = generate_user()
    u2, pwd2 = generate_user()
    channel = generate_an_email_channel(u1.id)
    # Notification owned by User 1
    notification = generate_notification(
        u1.id,
        channel.id,
        channel.type,
    )

    # User 2 login
    token2 = login(client, u2.email, pwd2)

    r = client.get(
        f"/notifications/{notification.id}",
        headers={"Authorization": f"Bearer {token2}"},
    )
    assert r.status_code == status.HTTP_404_NOT_FOUND


def test_update_notification(client):
    user, pwd = generate_user()
    channel = generate_an_email_channel(user.id)
    notification = generate_notification(
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
    r = client.patch(
        f"/notifications/{notification.id}",
        json=EDIT_JSON,
    )
    assert r.status_code == status.HTTP_401_UNAUTHORIZED

    token = login(client, user.email, pwd)

    # Check unchanged
    r = client.get(
        f"/notifications/{notification.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == status.HTTP_200_OK
    data_before = r.json()
    assert data_before["id"] == notification.id
    assert data_before["title"] == notification.title
    assert data_before["content"] == notification.content

    # Update
    r = client.patch(
        f"/notifications/{notification.id}",
        headers={"Authorization": f"Bearer {token}"},
        json=EDIT_JSON,
    )
    assert r.status_code == status.HTTP_200_OK
    data_update = r.json()
    assert data_update["id"] == notification.id

    # Check updated
    r = client.get(
        f"/notifications/{notification.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == status.HTTP_200_OK
    data_after = r.json()
    assert data_after["id"] == notification.id
    assert data_after["title"] == EDIT_JSON["title"]
    assert data_after["content"] == EDIT_JSON["content"]


def test_update_notification_ownership(client):
    u1, pwd1 = generate_user()
    u2, pwd2 = generate_user()
    channel = generate_an_email_channel(u1.id)
    # Notification owned by User 1
    notification = generate_notification(
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

    token2 = login(client, u2.email, pwd2)

    r = client.patch(
        f"/notifications/{notification.id}",
        headers={"Authorization": f"Bearer {token2}"},
        json=EDIT_JSON_NOT_AUTHORIZED,
    )
    assert r.status_code == status.HTTP_404_NOT_FOUND

    token1 = login(client, u1.email, pwd1)

    # Check unchanged
    r = client.get(
        f"/notifications/{notification.id}",
        headers={"Authorization": f"Bearer {token1}"},
    )
    assert r.status_code == status.HTTP_200_OK
    data_before = r.json()
    assert data_before["id"] == notification.id
    assert data_before["title"] == notification.title
    assert data_before["content"] == notification.content

    # Update
    r = client.patch(
        f"/notifications/{notification.id}",
        headers={"Authorization": f"Bearer {token1}"},
        json=EDIT_JSON_AUTHORIZED,
    )
    assert r.status_code == status.HTTP_200_OK
    data_update = r.json()
    assert data_update["id"] == notification.id

    # Check updated
    r = client.get(
        f"/notifications/{notification.id}",
        headers={"Authorization": f"Bearer {token1}"},
    )
    assert r.status_code == status.HTTP_200_OK
    data_after = r.json()
    assert data_after["id"] == notification.id
    assert data_after["title"] == EDIT_JSON_AUTHORIZED["title"]
    assert data_after["content"] == EDIT_JSON_AUTHORIZED["content"]


def test_delete_notification(client):
    user, pwd = generate_user()
    channel = generate_an_email_channel(user.id)
    notification = generate_notification(
        user.id,
        channel.id,
        channel.type,
    )

    # Not authenticated
    r = client.delete(
        f"/notifications/{notification.id}",
    )
    assert r.status_code == status.HTTP_401_UNAUTHORIZED

    token = login(client, user.email, pwd)

    # Check unchanged
    r = client.get(
        f"/notifications/{notification.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == status.HTTP_200_OK
    data_before = r.json()
    assert data_before["id"] == notification.id
    assert data_before["title"] == notification.title
    assert data_before["content"] == notification.content

    # Delete
    r = client.delete(
        f"/notifications/{notification.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == status.HTTP_204_NO_CONTENT

    # Check deleted
    r = client.get(
        f"/notifications/{notification.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == status.HTTP_404_NOT_FOUND


def test_delete_notification_ownership(client):
    u1, pwd1 = generate_user()
    u2, pwd2 = generate_user()
    channel = generate_an_email_channel(u1.id)
    # Notification owned by User 1
    notification = generate_notification(
        u1.id,
        channel.id,
        channel.type,
    )

    # User 2 login
    token2 = login(client, u2.email, pwd2)

    # Try delete
    r = client.delete(
        f"/notifications/{notification.id}",
        headers={"Authorization": f"Bearer {token2}"},
    )
    assert r.status_code == status.HTTP_404_NOT_FOUND

    token1 = login(client, u1.email, pwd1)

    # Check unchanged
    r = client.get(
        f"/notifications/{notification.id}",
        headers={"Authorization": f"Bearer {token1}"},
    )
    assert r.status_code == status.HTTP_200_OK
    data_before = r.json()
    assert data_before["id"] == notification.id
    assert data_before["title"] == notification.title
    assert data_before["content"] == notification.content

    # Delete
    r = client.delete(
        f"/notifications/{notification.id}",
        headers={"Authorization": f"Bearer {token1}"},
    )
    assert r.status_code == status.HTTP_204_NO_CONTENT

    # Check deleted
    r = client.get(
        f"/notifications/{notification.id}",
        headers={"Authorization": f"Bearer {token1}"},
    )
    assert r.status_code == status.HTTP_404_NOT_FOUND
