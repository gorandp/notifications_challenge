from app.core.channel_service import IChannelService


class ChannelService(IChannelService):
    def __init__(self, repository):
        self.repository = repository

    async def create_channel(self, channel):
        return await self.repository.add(channel)

    async def get_channel(self, channel_id=None, user_id=None, channel_type=None):
        return await self.repository.get(channel_id, user_id, channel_type)

    async def get_all_channels(self, user_id):
        return await self.repository.get_all(user_id)

    async def update_channel(self, channel_id, channel):
        return await self.repository.update(channel_id, channel)

    async def delete_channel(self, channel_id):
        return await self.repository.delete(channel_id)
