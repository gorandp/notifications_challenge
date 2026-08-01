from httpx import AsyncClient


async def login(client: AsyncClient, username: str, pwd: str):
    r = await client.post(
        "/token",
        data={
            "username": username,
            "password": pwd,
        },
    )
    data = r.json()
    if "access_token" not in data:
        raise ValueError("Login failed")
    return data["access_token"]
