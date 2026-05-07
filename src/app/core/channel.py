from datetime import datetime, UTC
from dataclasses import dataclass, field
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
    sender_name: str | None = None
    inserted_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
