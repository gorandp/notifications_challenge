from app.core.user_service import IUserService


class UserService(IUserService):
    def __init__(self, user_repository):
        self.repository = user_repository

    async def create_user(self, user):
        return await self.repository.create_user(user)

    async def get_user(self, user_id):
        return await self.repository.get_by_id(user_id)

    async def get_user_by_email(self, email):
        return await self.repository.get_by_email(email)

    async def get_all_users(self):
        return await self.repository.get_all()

    async def update_user(self, user):
        return await self.repository.update_user(user)

    async def delete_user(self, user_id):
        return await self.repository.delete_user(user_id)
