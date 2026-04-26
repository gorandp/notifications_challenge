from abc import ABC, abstractmethod

from .user import User
from .notification import Notification
from .channel import Channel


class IDatabase(ABC):
    @abstractmethod
    async def create_user(self, user: User) -> User:
        pass

    @abstractmethod
    async def get_user(
        self,
        user_id: int | None = None,
        user_email: str | None = None,
    ) -> User | None:
        pass

    @abstractmethod
    async def get_all_users(self) -> list[User]:
        pass

    @abstractmethod
    async def update_user(self, user_id: int, user: User) -> None:
        pass

    @abstractmethod
    async def delete_user(self, user_id: int) -> None:
        pass

    # @abstractmethod
    # async def add_notification(self, notification: Notification) -> None:
    #     pass

    @abstractmethod
    async def get_notification(self, notification_id: int) -> Notification | None:
        pass

    @abstractmethod
    async def get_all_notifications_by_user_id(
        self, user_id: int
    ) -> list[Notification]:
        pass

    # @abstractmethod
    # async def update_notification(self, notification: Notification) -> None:
    #     pass

    # @abstractmethod
    # async def delete_notification(self, notification_id: int) -> None:
    #     pass

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
    async def get_all_channels(
        self,
        user_id: int | None = None,
    ):
        pass

    @abstractmethod
    async def update_channel(
        self,
        channel_id: int,
        channel: Channel,
    ) -> None:
        pass

    @abstractmethod
    async def delete_channel(self, channel_id: int) -> None:
        pass
