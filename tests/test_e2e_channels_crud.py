from fastapi import status

from app.external.fastapi_app.context import channel_service_ctx
from db_data import (
    generate_user,
    generate_an_email_channel,
    generate_a_sms_channel,
)
from auth import login


def test_create_channel(client):
    user, pwd = generate_user()
    JSON_BODY = {"": ""}

    r = client.post("/channels", json=JSON_BODY)
    assert r.status_code == status.HTTP_401_UNAUTHORIZED

    token = login(client, user.email, pwd)

    # Check unchanged
    r = client.get(
        "/channels",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == status.HTTP_200_OK
    data_before = r.json()
    assert isinstance(data_before, list)
    assert len(data_before) == 0

    # Create notification
    r = client.post(
        "/channels",
        headers={"Authorization": f"Bearer {token}"},
        json=JSON_BODY,
    )
    assert r.status_code == status.HTTP_201_CREATED
    data_create = r.json()
    assert "id" in data_create
    new_channel_id = data_create["id"]

    # Check created
    r = client.get(
        "/channels",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == status.HTTP_200_OK
    data_after = r.json()
    assert isinstance(data_after, list)
    assert len(data_after) == 1
    assert data_after[0]["id"] == new_channel_id


def test_get_channels(client):
    user, pwd = generate_user()

    # Unauthenticated
    r = client.get("/channels")
    assert r.status_code == status.HTTP_401_UNAUTHORIZED

    token = login(client, user.email, pwd)

    # Authenticated
    r = client.get(
        "/channels",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    assert isinstance(data, list)
    assert len(data) == 0
    assert data == []

    channel_email = generate_an_email_channel(user.id)

    r = client.get(
        "/channels",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["id"] == channel_email.id

    channel_sms = generate_a_sms_channel(user.id)

    r = client.get(
        "/channels",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    assert isinstance(data, list)
    assert len(data) == 2
    all_ids = sorted([c["id"] for c in data])
    all_ids_db = sorted([channel_email.id, channel_sms.id])
    assert all_ids == all_ids_db


def test_get_channel(client):
    user, pwd = generate_user()
    channel = generate_an_email_channel(user.id)

    token = login(client, user.email, pwd)

    r = client.get(
        f"/channels/{channel.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    assert data["id"] == channel.id


def test_get_channels_ownership(client):
    u1, pwd1 = generate_user()
    u2, pwd2 = generate_user()
    channel1 = generate_an_email_channel(u1.id)

    token1 = login(client, u1.email, pwd1)

    r = client.get(
        "/channels",
        headers={"Authorization": f"Bearer {token1}"},
    )
    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    assert len(data) == 1
    assert data[0]["id"] == channel1.id

    token2 = login(client, u2.email, pwd2)

    r = client.get(
        "/channels",
        headers={"Authorization": f"Bearer {token2}"},
    )
    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    assert len(data) == 0


def test_get_channel_ownership(client):
    u1, pwd1 = generate_user()
    u2, pwd2 = generate_user()
    channel1 = generate_an_email_channel(u1.id)

    token2 = login(client, u2.email, pwd2)

    r = client.get(
        f"/channels/{channel1.id}",
        headers={"Authorization": f"Bearer {token2}"},
    )
    assert r.status_code == status.HTTP_404_NOT_FOUND

    token1 = login(client, u1.email, pwd1)

    r = client.get(
        f"/channels/{channel1.id}",
        headers={"Authorization": f"Bearer {token1}"},
    )
    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    assert data["id"] == channel1.id


async def test_update_channel(client):
    user, pwd = generate_user()
    channel = generate_an_email_channel(user.id)
    channel_service = channel_service_ctx.get()
    EDIT_JSON = {"credential_pass": "123456789123456789AAAABBBB"}
    assert channel.credential_pass != EDIT_JSON["credential_pass"]
    EDIT_JSON_2 = {
        "resource_url": "my-new-email-resource.com",
        "port_url": 999,
    }
    assert channel.resource_url != EDIT_JSON_2["resource_url"]
    assert channel.port_url != EDIT_JSON_2["port_url"]

    # Not authenticated
    r = client.patch(
        f"/channels/{channel.id}",
        json=EDIT_JSON,
    )
    assert r.status_code == status.HTTP_401_UNAUTHORIZED

    # Check unchanged
    ch = await channel_service.get_channel(channel.id)
    assert ch.credential_pass == channel.credential_pass

    token = login(client, user.email, pwd)

    # Check returned data
    r = client.get(
        f"/channels/{channel.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == status.HTTP_200_OK
    data_before = r.json()
    assert data_before["id"] == channel.id
    assert data_before["resource_url"] == channel.resource_url
    assert data_before["port_url"] == channel.port_url
    # This data shouldn't be returned
    assert "credential_username" not in data_before
    assert "credential_pass" not in data_before

    # Update
    r = client.patch(
        f"/channels/{channel.id}",
        headers={"Authorization": f"Bearer {token}"},
        json=EDIT_JSON,
    )
    assert r.status_code == status.HTTP_200_OK
    data_update = r.json()
    assert data_update["id"] == channel.id

    # Check updated
    ch = await channel_service.get_channel(channel.id)
    assert ch.credential_pass == EDIT_JSON["credential_pass"]

    # Update
    r = client.patch(
        f"/channels/{channel.id}",
        headers={"Authorization": f"Bearer {token}"},
        json=EDIT_JSON_2,
    )

    # Check updated
    r = client.get(
        f"/channels/{channel.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == status.HTTP_200_OK
    data_after = r.json()
    assert data_after["id"] == channel.id
    assert data_after["resource_url"] == EDIT_JSON["resource_url"]
    assert data_after["port_url"] == EDIT_JSON["port_url"]


def test_update_channel_ownership(client):
    u1, pwd1 = generate_user()
    u2, pwd2 = generate_user()
    channel1 = generate_an_email_channel(u1.id)
    EDIT_JSON_NOT_AUTHORIZED = {
        "resource_url": "not-authorized-new-url.com",
        "port_url": 1,
    }
    assert channel1.resource_url != EDIT_JSON_NOT_AUTHORIZED["resource_url"]
    assert channel1.port_url != EDIT_JSON_NOT_AUTHORIZED["port_url"]
    EDIT_JSON_AUTHORIZED = {
        "resource_url": "ok.com",
        "port_url": 1234,
    }
    assert channel1.resource_url != EDIT_JSON_AUTHORIZED["resource_url"]
    assert channel1.port_url != EDIT_JSON_AUTHORIZED["port_url"]

    token2 = login(client, u2.email, pwd2)

    r = client.patch(
        f"/channels/{channel1.id}",
        headers={"Authorization": f"Bearer {token2}"},
        json=EDIT_JSON_NOT_AUTHORIZED,
    )
    assert r.status_code == status.HTTP_404_NOT_FOUND

    token1 = login(client, u1.email, pwd1)

    # Check unchanged
    r = client.get(
        f"/channels/{channel1.id}",
        headers={"Authorization": f"Bearer {token1}"},
    )
    assert r.status_code == status.HTTP_200_OK
    data_before = r.json()
    assert data_before["id"] == channel1.id
    assert data_before["resource_url"] == channel1.resource_url
    assert data_before["port_url"] == channel1.port_url

    # Update
    r = client.patch(
        f"/channels/{channel1.id}",
        headers={"Authorization": f"Bearer {token1}"},
        json=EDIT_JSON_AUTHORIZED,
    )
    assert r.status_code == status.HTTP_200_OK
    data_update = r.json()
    assert data_update["id"] == channel1.id

    # Check updated
    r = client.get(
        f"/channels/{channel1.id}",
        headers={"Authorization": f"Bearer {token1}"},
    )
    assert r.status_code == status.HTTP_200_OK
    data_before = r.json()
    assert data_before["id"] == channel1.id
    assert data_before["resource_url"] == EDIT_JSON_AUTHORIZED["resource_url"]
    assert data_before["port_url"] == EDIT_JSON_AUTHORIZED["port_url"]


def test_delete_channel(client):
    user, pwd = generate_user()
    channel = generate_an_email_channel(user.id)

    # Not authenticated
    r = client.delete(
        f"/channels/{channel.id}",
    )
    assert r.status_code == status.HTTP_401_UNAUTHORIZED

    token = login(client, user.email, pwd)

    # Check unchanged
    r = client.get(
        f"/channels/{channel.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == status.HTTP_200_OK
    data_before = r.json()
    assert data_before["id"] == channel.id

    # Delete
    r = client.delete(
        f"/channels/{channel.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == status.HTTP_204_NO_CONTENT

    # Check deleted
    r = client.get(
        f"/channels/{channel.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == status.HTTP_404_NOT_FOUND


def test_delete_notification_ownership(client):
    u1, pwd1 = generate_user()
    u2, pwd2 = generate_user()
    channel1 = generate_an_email_channel(u1.id)

    token2 = login(client, u2.email, pwd2)

    # Try delete
    r = client.delete(
        f"/channels/{channel1.id}",
        headers={"Authorization": f"Bearer {token2}"},
    )
    assert r.status_code == status.HTTP_404_NOT_FOUND

    token1 = login(client, u1.email, pwd1)

    # Check unchanged
    r = client.get(
        f"/channels/{channel1.id}",
        headers={"Authorization": f"Bearer {token1}"},
    )
    assert r.status_code == status.HTTP_200_OK
    data_before = r.json()
    assert data_before["id"] == channel1.id

    # Delete
    r = client.delete(
        f"/channels/{channel1.id}",
        headers={"Authorization": f"Bearer {token1}"},
    )
    assert r.status_code == status.HTTP_204_NO_CONTENT

    # Check deleted
    r = client.get(
        f"/channels/{channel1.id}",
        headers={"Authorization": f"Bearer {token1}"},
    )
    assert r.status_code == status.HTTP_404_NOT_FOUND
