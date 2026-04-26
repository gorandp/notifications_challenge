from app.core.notification_service import INotificationService


class NotificationService(INotificationService):
    def __init__(self, notification_repository):
        self.repository = notification_repository

    async def create_notification(self, notification):
        return await self.repository.add(notification)

    async def get_notification(self, notification_id):
        return await self.repository.get_by_id(notification_id)

    async def get_all_notifications_from_user(self, user_id):
        return await self.repository.get_all_by_user_id(user_id)

    async def update_notification(self, notification_id, notification):
        return await self.repository.update(notification_id, notification)

    async def delete_notification(self, notification_id):
        return await self.repository.delete(notification_id)
