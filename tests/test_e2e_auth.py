# Register
# Login
# Authorization in endpoints
from fastapi import status

from app.external.fastapi_app.context import db_session
from app.external.database import database_models as models
from app.external.fastapi_app.auth import hash_password


def _create_test_user() -> tuple[models.UserModel, str]:
    """Create a test user

    Returns:
        tuple[models.User, str]: Returns the user and original password
    """
    db = db_session.get()
    pwd = "Password123!"
    password_hash = hash_password(pwd)
    new_user = models.UserModel(
        email="test@example.com",
        password_hash=password_hash,
        enabled=True,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user, pwd


def test_unauthenticated(client):
    r = client.get("/testAuth")
    assert r.status_code == status.HTTP_401_UNAUTHORIZED


def test_login(client):
    u, pwd = _create_test_user()
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
    u, pwd = _create_test_user()
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
