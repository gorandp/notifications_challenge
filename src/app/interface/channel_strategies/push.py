import httpx

from app.core.channel import ChannelType
from app.core.channel_strategy import IChannelStrategy


class PushChannel(IChannelStrategy):
    strategy_type = ChannelType.PUSH.value

    def __init__(self, channel):
        self.channel = channel

    async def _connect(self):
        pass

    async def _close(self):
        pass

    async def send(self, notification):
        if self.channel.resource_url == "api.onesignal.com":
            # https://documentation.onesignal.com/reference/push-notification
            await httpx.post(
                self.channel.resource_url,
                headers={
                    "Authorization": f"Key {self.channel.credential_pass}",
                },
                json={
                    "target_channel": "push",
                    "include_subscription_ids": notification.recipient,
                    "headings": {
                        "en": notification.title,
                        "es": notification.title,
                    },
                    "contents": {
                        "en": notification.content,
                        "es": notification.content,
                    },
                },
            )
        else:
            raise NotImplementedError("Provider not implemented yet")

    @classmethod
    def validate_notification(cls, notification):
        if len(notification.title) > 128:
            raise ValueError("Title is too long")
        if len(notification.content) > 256:
            raise ValueError("Content too long")
