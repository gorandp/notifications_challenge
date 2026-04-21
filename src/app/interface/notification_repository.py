from app.core.notification_repository import INotificationRepository


class NotificationRepository(INotificationRepository):
    def __init__(self, db):
        self.db = db
        self.PAGE_SIZE = 50

    async def get_by_id(self, id):
        return await self.db.get_notification(id)

    async def get_all_by_user_id(self, user_id):
        return await self.db.get_all_notifications_by_user_id(user_id)
