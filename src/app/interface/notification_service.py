from app.core.notification_service import INotificationService

from .channel_strategies import CHANNEL_STRATEGIES


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

    async def validate_notification(self, notification):
        c_strategy = CHANNEL_STRATEGIES.get(notification.channel_type)
        if not c_strategy:
            raise ValueError(
                f"Channel type '{notification.channel_type}' "
                + "doesn't have a strategy defined"
            )
        return await c_strategy.validate_notification(notification)

    async def send_notification(self, notification):
        c_strategy = CHANNEL_STRATEGIES.get(notification.channel_type)
        if not c_strategy:
            raise ValueError(
                f"Channel type '{notification.channel_type}' "
                + "doesn't have a strategy defined"
            )
        return await c_strategy.send(notification)
