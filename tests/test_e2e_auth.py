# Register
# Login
# Authorization in endpoints
import pytest
from fastapi import status

from db_data import generate_user
from auth import login


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


def test_register(client):
    u, pwd = generate_user()
    NEW_USER = {
        "username": "test1234567890@example.com",
        "password": "password1234567890",
    }
    assert u.email != NEW_USER["username"]
    assert pwd != NEW_USER["password"]

    # Test already existent user email
    r = client.post("/register", json={"username": u.email, "password": "password"})
    assert r.status_code == status.HTTP_400_BAD_REQUEST

    with pytest.raises(ValueError):
        login(client, u.email, "password")

    token = login(client, u.email, pwd)
    assert isinstance(token, str)

    # Register
    r = client.post("/register", json=NEW_USER)
    assert r.status_code == status.HTTP_201_CREATED

    token_new = login(client, NEW_USER["username"], NEW_USER["password"])
    assert isinstance(token_new, str)
