# Register
# Login
# Authorization in endpoints
import hashlib

from app.external.database.main import db_session
from app.external.database import database_models as models


def _create_test_user() -> tuple[models.User, str]:
    """Create a test user

    Returns:
        tuple[models.User, str]: Returns the user and original password
    """
    db = db_session.get()
    pwd = "password123"
    password_hash = hashlib.sha256(pwd.encode("utf-8")).hexdigest()
    new_user = models.User(
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
    assert r.status_code == 401


def test_login(client):
    u, pwd = _create_test_user()
    r = client.post(
        "/login",
        json={
            "email": u.email,
            "password": pwd,
        },
    )
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_authenticated_endpoint(client):
    u, pwd = _create_test_user()
    r = client.post(
        "/login",
        json={
            "email": u.email,
            "password": pwd,
        },
    )
    assert r.status_code == 200
    assert "access_token" in r.json()
    token = r.json()["access_token"]
    r = client.get("/testAuth", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json() == {"success": True}
