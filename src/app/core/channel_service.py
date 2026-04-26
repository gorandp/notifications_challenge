from abc import ABC, abstractmethod

from .channel import Channel
from .channel_repository import IChannelRepository


class IChannelService(ABC):
    repository: IChannelRepository

    @abstractmethod
    def __init__(self, repository: IChannelRepository):
        pass

    @abstractmethod
    async def create_channel(self, channel: Channel) -> Channel:
        pass

    @abstractmethod
    async def get_channel(
        self,
        channel_id: int | None = None,
        user_id: int | None = None,
        channel_type: str | None = None,
    ) -> Channel:
        pass

    @abstractmethod
    async def get_all_channels(self, user_id: int) -> list[Channel]:
        pass

    @abstractmethod
    async def update_channel(self, channel_id: int, channel: Channel) -> None:
        pass

    @abstractmethod
    async def delete_channel(self, channel_id: int) -> None:
        pass
