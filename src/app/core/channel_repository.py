from abc import ABC, abstractmethod

from .channel import Channel
from .database import IDatabase


class IChannelRepository(ABC):
    db: IDatabase

    @abstractmethod
    def __init__(self, db: IDatabase):
        pass

    @abstractmethod
    async def add(self, channel: Channel) -> Channel:
        """Add channel to repository"""

    @abstractmethod
    async def get(
        self,
        # Get by channel ID
        channel_id: int | None = None,
        # Get by user ID
        user_id: int | None = None,
        # Filter by channel type
        channel_type: str | None = None,
    ) -> Channel:
        """Get channel"""

    @abstractmethod
    async def get_all(
        self,
        user_id: int,
    ) -> list[Channel]:
        """Get all channels"""

    @abstractmethod
    async def update(
        self,
        channel_id: int,
        channel: Channel,
    ) -> None:
        """Update channel"""

    @abstractmethod
    async def delete(self, channel_id: str) -> None:
        """Delete channel"""
