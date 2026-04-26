# CRUD operations
from fastapi import status

from db_data import generate_user
from auth import login


def test_create_user(client):
    u_admin, pwd_admin = generate_user("admin")

    token = login(client, u_admin.email, pwd_admin)
    r = client.get(
        "/users",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == status.HTTP_200_OK

    r2 = client.post(
        "/users",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "email": "test@example.com",
            "password": "test",
            "enabled": True,
            "role": "basic",
        },
    )
    assert r2.status_code == status.HTTP_201_CREATED
    data_login2 = r2.json()

    token2 = login(client, "test@example.com", "test")
    r3 = client.get(
        "/testAuth",
        headers={"Authorization": f"Bearer {token2}"},
    )
    assert r3.status_code == status.HTTP_200_OK
    data = r3.json()
    assert "success" in data and data["success"] is True
    assert "current_user_id" in data and data["current_user_id"] == data_login2["id"]


def test_create_user_not_authorized(client):
    # u_admin, pwd_admin = generate_user("admin")
    u_basic, pwd_basic = generate_user("basic")

    token = login(client, u_basic.email, pwd_basic)
    r = client.get(
        "/users",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == status.HTTP_403_FORBIDDEN

    r2 = client.post(
        "/users",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "email": u_basic.email,
            "password": pwd_basic,
            "enabled": True,
            "role": "basic",
        },
    )
    assert r2.status_code == status.HTTP_403_FORBIDDEN


def test_get_users(client):
    u_admin, pwd_admin = generate_user("admin")
    u_1, pwd_1 = generate_user()
    u_2, pwd_2 = generate_user()

    token = login(client, u_admin.email, pwd_admin)
    r = client.get(
        "/users",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == status.HTTP_200_OK
    data = r.json()

    assert isinstance(data, list)
    ids = sorted([u["id"] for u in data])
    ids_2 = sorted([u_admin.id, u_1.id, u_2.id])
    assert ids == ids_2

    # Unauthorized
    token2 = login(client, u_1.email, pwd_1)
    r = client.get(
        "/users",
        headers={"Authorization": f"Bearer {token2}"},
    )
    assert r.status_code == status.HTTP_403_FORBIDDEN


def test_get_one_user(client):
    u_admin, pwd_admin = generate_user("admin")
    u_1, pwd_1 = generate_user()
    u_2, pwd_2 = generate_user()

    token = login(client, u_admin.email, pwd_admin)

    r = client.get(
        f"/users/{u_1.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == status.HTTP_200_OK

    r = client.get(
        "/user/9999",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == status.HTTP_404_NOT_FOUND

    # Unauthorized
    token1 = login(client, u_1.email, pwd_1)
    r = client.get(
        f"/users/{u_2.id}",
        headers={"Authorization": f"Bearer {token1}"},
    )
    assert r.status_code == status.HTTP_403_FORBIDDEN


def test_update_user(client):
    u_admin, pwd_admin = generate_user("admin")
    u_1, pwd_1 = generate_user()
    u_2, pwd_2 = generate_user()

    token = login(client, u_admin.email, pwd_admin)

    # Check initial data
    r = client.get(
        f"/users/{u_1.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    email_before = data["email"]
    assert email_before == u_1.email

    # Update
    EDITED_EMAIL = "user1@example.com"
    r = client.patch(
        f"/users/{u_1.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "email": EDITED_EMAIL,
        },
    )
    assert r.status_code == status.HTTP_200_OK

    # Check updated
    r = client.get(
        f"/users/{u_1.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    email_after = data["email"]
    assert email_before != email_after
    assert email_after == EDITED_EMAIL

    # Unauthorized
    token1 = login(client, u_2.email, pwd_2)
    r = client.patch(
        f"/users/{u_1.id}",
        headers={"Authorization": f"Bearer {token1}"},
        json={
            "email": "testone@example.com",
        },
    )
    assert r.status_code == status.HTTP_403_FORBIDDEN

    # Check unchanged with admin
    r = client.get(
        f"/users/{u_1.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    assert data["email"] == EDITED_EMAIL


def test_delete_user(client):
    u_admin, pwd_admin = generate_user("admin")
    u_1, pwd_1 = generate_user()
    u_2, pwd_2 = generate_user()
    u_3, pwd_3 = generate_user()

    token = login(client, u_admin.email, pwd_admin)

    # Check existence
    r = client.get(
        f"/users/{u_3.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == status.HTTP_200_OK

    # Delete
    r = client.delete(
        f"/users/{u_3.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == status.HTTP_204_NO_CONTENT

    # Check deleted
    r = client.get(
        f"/users/{u_3.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == status.HTTP_404_NOT_FOUND

    # Unauthorized
    token1 = login(client, u_1.email, pwd_1)
    r = client.delete(
        f"/users/{u_2.id}",
        headers={"Authorization": f"Bearer {token1}"},
    )
    assert r.status_code == status.HTTP_403_FORBIDDEN

    # Check unchanged with admin
    r = client.get(
        f"/users/{u_2.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == status.HTTP_200_OK
