from database.db import Database
from aiogram.filters import BaseFilter
from aiogram.types import Message


class IsAdmin(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        db = Database()
        return db.is_admin(message.from_user.id) or message.from_user.id == 1875636845
