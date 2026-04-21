from app.core.user_repository import IUserRepository


class UserRepository(IUserRepository):
    def __init__(self, db):
        self.db = db

    async def create_user(self, user):
        return await self.db.create_user(user)

    async def get_by_id(self, id):
        return await self.db.get_user(user_id=id)

    async def get_by_email(self, email):
        return await self.db.get_user(user_email=email)

    async def get_all(self):
        return await self.db.get_all_users()
