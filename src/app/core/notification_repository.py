from abc import ABC, abstractmethod

from .notification import Notification
from .database import IDatabase


class INotificationRepository(ABC):
    db: IDatabase

    @abstractmethod
    def __init__(self, db: IDatabase):
        pass

    @abstractmethod
    async def add(self, notification: Notification) -> Notification:
        """Adds a new notification and returns it with
        default values if possible and its ID.

        Args:
            notification (Notification): Data to insert

        Returns:
            Notification: The same notification with default values
                and ID
        """

    @abstractmethod
    async def get_by_id(self, id: int) -> Notification | None:
        """Returns a notification with the given id"""

    @abstractmethod
    async def get_all_by_user_id(self, user_id: int) -> list[Notification]:
        """Returns all notifications by a user"""

    @abstractmethod
    async def update(self, notification_id: int, notification: Notification) -> None:
        """Update an existent notification"""

    @abstractmethod
    async def update_status(
        self,
        notification_id: int,
        notification_status: int,
    ) -> None:
        """Update notification status"""

    @abstractmethod
    async def delete(self, notification_id: int):
        """Delete a notification"""
