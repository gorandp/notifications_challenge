# Create
# Edit
# Delete
# Query all
from fastapi import status

from db_data import generate_user, generate_notification
from auth import login


def test_auth_get_notification(client):
    r = client.get("/notifications")
    assert r.status_code == status.HTTP_401_UNAUTHORIZED

    user, pwd = generate_user()
    token = login(client, user.email, pwd)
    r = client.get(
        "/notifications",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == status.HTTP_200_OK
    assert r.json() == []


def test_get_notifications(client):
    user, pwd = generate_user()
    notification = generate_notification(user.id)
    token = login(client, user.email, pwd)

    r = client.get(
        "/notifications",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    assert data[0]["id"] == notification.id
