# Register
# Login
# Authorization in endpoints
from src.app.external.fastapi_app.database import db_session
from src.app.external.database import database_models as models
from src.app.external.fastapi_app.config import JWTConfig
import hashlib


def test_unauthenticated(client):
    r = client.get("/testAuth")
    assert r.status_code == 401


def test_login(client):
    JWTConfig.set_secret("secret123")
    db = db_session.get()
    password_hash = hashlib.sha256("password123".encode("utf-8")).hexdigest()
    new_user = models.User(
        email="test@example.com", password_hash=password_hash, enabled=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    r = client.post(
        "/login", json={"email": "test@example.com", "password": "password123"}
    )

    assert r.status_code == 200
    assert "access_token" in r.json()
