from datetime import datetime, UTC
from dataclasses import dataclass, field
from enum import IntEnum


class NotifStatus(IntEnum):
    PENDING = 0
    SENT = 1
    SUCCESS = 2


@dataclass
class Notification:
    user_id: int
    channel_id: int
    channel_type: str
    status: int
    recipient: str
    id: int | None = None
    title: str = ""
    content: str = ""
    inserted_at: datetime = field(default_factory=lambda: datetime.now(UTC))
