from app.core.channel import ChannelType
from app.core.channel_strategy import IChannelStrategy

from .email import EmailChannel
from .sms import SmsChannel
from .push import PushChannel


CHANNEL_STRATEGIES: dict[str, type[IChannelStrategy]] = {
    ChannelType.EMAIL.value: EmailChannel,
    ChannelType.SMS.value: SmsChannel,
    ChannelType.PUSH.value: PushChannel,
}
