import re
import httpx

from app.core.channel import ChannelType
from app.core.channel_strategy import IChannelStrategy


PHONE_NUMBER_REGEX = re.compile(r"^\d{1,3}_\d{1}_\d{10}$")


class SmsChannel(IChannelStrategy):
    strategy_type = ChannelType.SMS.value

    def __init__(self, channel):
        self.channel = channel

    async def _connect(self):
        pass

    async def _close(self):
        pass

    async def send(self, notification):
        if self.channel.resource_url == "api.onesignal.com":
            # https://documentation.onesignal.com/reference/sms
            content = notification.content
            if notification.title:
                content = notification.title + "\n\n" + notification.content
            await httpx.post(
                self.channel.resource_url,
                headers={
                    "Authorization": f"Key {self.channel.credential_pass}",
                },
                json={
                    "app_id": self.channel.credential_user,
                    "contents": {
                        "en": content,
                        "es": content,
                    },
                    "target_channel": "sms",
                    "include_phone_numbers": [
                        notification.recipient,
                    ],
                },
            )
        else:
            raise NotImplementedError("Provider not implemented yet")

    @classmethod
    def validate_notification(cls, notification):
        if len(notification.content) > 160:
            raise ValueError("Content should be less than 160 characters")
        if not PHONE_NUMBER_REGEX.match(notification.recipient):
            raise ValueError("Recipient must have a valid phone number")
