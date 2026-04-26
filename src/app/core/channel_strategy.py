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
    async def connect(self):
        """Stablish connection"""

    @abstractmethod
    async def close(self):
        """Close connection"""

    @abstractmethod
    async def send(self, notification: Notification):
        """Send notification"""
