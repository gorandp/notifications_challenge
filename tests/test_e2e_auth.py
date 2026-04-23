# Register
# Login
# Authorization in endpoints
from fastapi import status

from db_data import generate_user


def test_unauthenticated(client):
    r = client.get("/testAuth")
    assert r.status_code == status.HTTP_401_UNAUTHORIZED


def test_login(client):
    u, pwd = generate_user()
    r = client.post(
        "/token",
        data={
            "username": u.email,
            "password": "pwd",  # Wrong password
        },
    )
    assert r.status_code == status.HTTP_400_BAD_REQUEST

    r = client.post(
        "/token",
        data={
            "username": u.email,
            "password": pwd,
        },
    )
    assert r.status_code == status.HTTP_200_OK
    assert "access_token" in r.json()


def test_authenticated_endpoint(client):
    u, pwd = generate_user()
    r = client.post(
        "/token",
        data={
            "username": u.email,
            "password": pwd,
        },
    )
    assert r.status_code == status.HTTP_200_OK
    assert "access_token" in r.json()
    token = r.json()["access_token"]
    r = client.get(
        "/testAuth",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    assert "success" in data and data["success"] is True
    assert "current_user_id" in data and data["current_user_id"] == u.id
