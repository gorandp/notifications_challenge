from app.core.channel_repository import IChannelRepository


class ChannelRepository(IChannelRepository):
    def __init__(self, db):
        self.db = db

    async def add(self, channel):
        return await self.db.create_channel(channel)

    async def get(self, channel_id=None, user_id=None, channel_type=None):
        return await self.db.get_channel(channel_id, user_id, channel_type)

    async def get_all(self, user_id):
        return await self.db.get_all_channels(user_id)

    async def update(self, channel_id, channel):
        return await self.db.update_channel(channel_id, channel)

    async def delete(self, channel_id):
        return await self.db.delete_channel(channel_id)
