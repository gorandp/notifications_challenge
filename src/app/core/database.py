from abc import ABC, abstractmethod

from .user import User
from .notification import Notification


class IDatabase(ABC):
    # @abstractmethod
    # async def add_user(self, user: User) -> None:
    #     pass

    @abstractmethod
    async def get_user(self, user_id: int) -> User | None:
        pass

    @abstractmethod
    async def get_all_users(self) -> list[User]:
        pass

    # @abstractmethod
    # async def update_user(self, user: User) -> None:
    #     pass

    # @abstractmethod
    # async def delete_user(self, user_id: int) -> None:
    #     pass

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
