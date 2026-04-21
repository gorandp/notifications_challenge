from abc import ABC, abstractmethod

from .user import User
from .database import IDatabase


class IUserRepository(ABC):
    db: IDatabase

    @abstractmethod
    def __init__(self, db: IDatabase):
        pass

    @abstractmethod
    async def create_user(self, user: User):
        """Create a new user"""

    @abstractmethod
    async def get_by_id(self, id: int) -> User | None:
        """Returns a user with the given id"""

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        """Returns a user with the given email"""

    @abstractmethod
    async def get_all(self) -> list[User]:
        """Returns all users"""

    @abstractmethod
    async def update_user(self, user: User):
        """Update user"""

    @abstractmethod
    async def delete_user(self, user_id: int):
        """Delete user"""
