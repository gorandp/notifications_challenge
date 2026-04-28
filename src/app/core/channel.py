from dataclasses import dataclass
from enum import StrEnum


class ChannelType(StrEnum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"


@dataclass
class Channel:
    user_id: int
    type: str
    credential_user: str
    credential_pass: str
    resource_url: str
    port_url: int
    id: str | None = None
