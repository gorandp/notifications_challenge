from app.core.user_service import IUserService


class UserService(IUserService):
    def __init__(self, user_repository):
        self.repository = user_repository

    async def get_user(self, user_id):
        return await self.repository.get_by_id(user_id)

    async def get_all_users(self):
        return await self.repository.get_all()
