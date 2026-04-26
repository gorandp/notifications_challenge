from abc import ABC, abstractmethod

from .notification import Notification
from .notification_repository import INotificationRepository


class INotificationService(ABC):
    repository: INotificationRepository

    @abstractmethod
    def __init__(self, notification_repository: INotificationRepository):
        pass

    @abstractmethod
    async def create_notification(self, notification: Notification) -> Notification:
        pass

    @abstractmethod
    async def get_notification(self, notification_id: int) -> Notification:
        pass

    @abstractmethod
    async def get_all_notifications_from_user(self, user_id: int) -> list[Notification]:
        pass

    @abstractmethod
    async def update_notification(
        self, notification_id: int, notification: Notification
    ) -> None:
        pass

    @abstractmethod
    async def delete_notification(self, notification_id: int) -> None:
        pass
