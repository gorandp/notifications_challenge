from datetime import datetime, UTC
from dataclasses import dataclass, field
from enum import IntEnum


class NotifStatus(IntEnum):
    PENDING = 0
    SENDING = 100
    SENT = 200
    SUCCESS = 201
    ERROR = 500


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
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    sent_at: datetime | None = None
