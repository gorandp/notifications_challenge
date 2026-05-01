from abc import ABC, abstractmethod

from .channel import Channel
from .notification import Notification


class IChannelStrategy(ABC):
    channel: Channel
    strategy_type: str  # sms, email, push

    @abstractmethod
    def __init__(self, channel: Channel):
        pass

    @abstractmethod
    async def _connect(self):
        """Stablish connection"""

    @abstractmethod
    async def _close(self):
        """Close connection"""

    @abstractmethod
    async def send(self, notification: Notification):
        """
        Stablish connection, validates notification, sends it and
        finally closes the connection
        """

    @classmethod
    @abstractmethod
    def validate_notification(cls, notification: Notification) -> None:
        """Validate that the notification can be sent via this channel type"""
