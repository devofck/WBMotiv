from aiogram.filters import BaseFilter
from aiogram.types import ChatJoinRequest
from database.db import Database


class IsChannelAdded(BaseFilter):
    async def __call__(self, request: ChatJoinRequest):
        db = Database()
        return str(request.chat.id) in db.get_channels_ids(request.chat.id)
