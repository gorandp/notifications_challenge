from abc import ABC, abstractmethod

from .user import User
from .user_repository import IUserRepository


class IUserService(ABC):
    repository: IUserRepository

    @abstractmethod
    def __init__(self, user_repository: IUserRepository):
        pass

    @abstractmethod
    async def get_user(self, user_id: int) -> User | None:
        pass

    @abstractmethod
    async def get_all_users(self) -> list[User]:
        pass
