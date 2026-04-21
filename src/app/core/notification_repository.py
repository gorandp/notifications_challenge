from abc import ABC, abstractmethod

from .notification import Notification
from .database import IDatabase


class INotificationRepository(ABC):
    db: IDatabase

    @abstractmethod
    def __init__(self, db: IDatabase):
        pass

    @abstractmethod
    async def get_by_id(self, id: int) -> Notification | None:
        """Returns a notification with the given id"""

    @abstractmethod
    async def get_all_by_user_id(self, user_id: int) -> list[Notification]:
        """Returns all notifications by a user"""
