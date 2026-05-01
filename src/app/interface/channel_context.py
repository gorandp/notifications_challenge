from app.core.channel_context import IChannelContext
from app.core.notification import NotifStatus

from .channel_strategies import CHANNEL_STRATEGIES


class ChannelContext(IChannelContext):
    def __init__(self, n_serv):
        self.n_serv = n_serv

    def get_strategy(self, channel):
        c_strategy_class = CHANNEL_STRATEGIES.get(channel.type)
        if not c_strategy_class:
            raise ValueError(
                f"Channel type '{channel.type}' doesn't have a strategy defined"
            )
        return c_strategy_class(channel)

    async def send(self, channel, notification):
        strategy = self.get_strategy(channel)
        await self.n_serv.update_notification_status(
            notification.id,
            NotifStatus.SENDING.value,
        )
        notification.status = NotifStatus.SENDING.value
        try:
            await strategy.send(notification)
        except Exception:
            await self.n_serv.update_notification_status(
                notification.id,
                NotifStatus.ERROR.value,
            )
            notification.status = NotifStatus.ERROR.value
            # Continue exception
            raise
        else:
            await self.n_serv.update_notification_status(
                notification.id,
                NotifStatus.SENT.value,
            )
            notification.status = NotifStatus.SENT.value
