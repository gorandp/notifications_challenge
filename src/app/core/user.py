from datetime import datetime, UTC
from dataclasses import dataclass, field


class ROLES:
    ADMIN = "admin"
    BASIC = "basic"


@dataclass
class User:
    email: str
    password_hash: str
    enabled: bool
    id: int | None = None
    role: str = "basic"
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
