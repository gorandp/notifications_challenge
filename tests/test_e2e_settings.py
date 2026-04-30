from fastapi import status

from db_data import generate_user
from auth import login


def test_get_settings(client):
    u1, pwd1 = generate_user()

    token1 = login(client, u1.email, pwd1)

    r = client.get(
        "/settings",
        headers={"Authorization": f"Bearer {token1}"},
    )
    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    assert data["email"] == u1.email


def test_update_settings(client):
    u1, pwd1 = generate_user()
    UPDATE_JSON = {
        "email": "mynewemail@test.com",
    }
    assert UPDATE_JSON["email"] != u1.email

    token1 = login(client, u1.email, pwd1)

    r = client.patch(
        "/settings",
        headers={"Authorization": f"Bearer {token1}"},
        json=UPDATE_JSON,
    )
    assert r.status_code == status.HTTP_200_OK

    r = client.get(
        "/settings",
        headers={"Authorization": f"Bearer {token1}"},
    )
    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    assert data["email"] == UPDATE_JSON["email"]
