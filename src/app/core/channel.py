from dataclasses import dataclass


@dataclass
class Channel:
    user_id: int
    type: str
    credential_user: str
    credential_pass: str
    resource_url: str
    port_url: int
    id: str | None = None
