from fastapi.testclient import TestClient


def login(client: TestClient, username: str, pwd: str):
    r = client.post(
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
