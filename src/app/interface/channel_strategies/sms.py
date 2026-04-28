from app.core.channel import ChannelType
from app.core.channel_strategy import IChannelStrategy


class SmsChannel(IChannelStrategy):
    strategy_type = ChannelType.SMS.value

    def __init__(self, channel):
        self.channel = channel

    async def connect(self):
        pass

    async def close(self):
        pass

    async def send(self, notification):
        pass
