from fastapi.testclient import TestClient


def login(client: TestClient, username: str, pwd: str):
    r = client.post(
        "/token",
        data={
            "username": username,
            "password": pwd,
        },
    )
    return r.json()["access_token"]
