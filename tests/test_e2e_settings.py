import pytest
from fastapi import status

from tests.db_data import generate_user
from tests.auth import login


@pytest.mark.anyio
async def test_get_settings(client):
    u1, pwd1 = await generate_user()

    token1 = await login(client, u1.email, pwd1)

    r = await client.get(
        "/settings",
        headers={"Authorization": f"Bearer {token1}"},
    )
    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    assert data["email"] == u1.email


@pytest.mark.anyio
async def test_update_settings(client):
    u1, pwd1 = await generate_user()
    UPDATE_JSON = {
        "email": "mynewemail@test.com",
    }
    assert UPDATE_JSON["email"] != u1.email

    token1 = await login(client, u1.email, pwd1)

    r = await client.patch(
        "/settings",
        headers={"Authorization": f"Bearer {token1}"},
        json=UPDATE_JSON,
    )
    assert r.status_code == status.HTTP_200_OK

    r = await client.get(
        "/settings",
        headers={"Authorization": f"Bearer {token1}"},
    )
    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    assert data["email"] == UPDATE_JSON["email"]
