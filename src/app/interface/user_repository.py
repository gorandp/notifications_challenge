from app.core.user_repository import IUserRepository


class UserRepository(IUserRepository):
    def __init__(self, db):
        self.db = db

    async def get_by_id(self, id):
        return await self.db.get_user(id)

    async def get_all(self):
        return await self.db.get_all_users()
