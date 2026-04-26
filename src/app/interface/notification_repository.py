from app.core.notification_repository import INotificationRepository


class NotificationRepository(INotificationRepository):
    def __init__(self, db):
        self.db = db
        self.PAGE_SIZE = 50

    async def add(self, notification):
        return await self.db.create_notification(notification)

    async def get_by_id(self, id):
        return await self.db.get_notification(id)

    async def get_all_by_user_id(self, user_id):
        return await self.db.get_all_notifications_by_user_id(user_id)

    async def update(self, notification_id, notification):
        return await self.db.update_notification(notification_id, notification)

    async def delete(self, notification_id):
        return await self.db.delete_notification(notification_id)
