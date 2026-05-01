import re

from app.core.channel import ChannelType
from app.core.channel_strategy import IChannelStrategy


PHONE_NUMBER_REGEX = re.compile(r"\d{1,3}_\d{1}_\d{10}")


class SmsChannel(IChannelStrategy):
    strategy_type = ChannelType.SMS.value

    def __init__(self, channel):
        self.channel = channel

    async def _connect(self):
        pass

    async def _close(self):
        pass

    async def send(self, notification):
        pass

    @classmethod
    def validate_notification(cls, notification):
        if len(notification.content) > 160:
            raise ValueError("Content should be less than 160 characters")
        if not PHONE_NUMBER_REGEX.match(notification.recipient):
            raise ValueError("Recipient must have a valid phone number")
