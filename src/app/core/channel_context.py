from abc import ABC, abstractmethod

from .channel import Channel
from .notification import Notification
from .notification_service import INotificationService
from .channel_strategy import IChannelStrategy


class IChannelContext(ABC):
    n_serv: INotificationService

    @abstractmethod
    def __init__(self, n_serv: INotificationService):
        pass

    @abstractmethod
    def get_strategy(self, channel: Channel) -> IChannelStrategy:
        pass

    @abstractmethod
    async def send(self, channel: Channel, notification: Notification) -> None:
        """Send a notification through the selected channel

        Args:
            channel (Channel): Selected channel
            notification (Notification): Notification to send
        """
        pass
