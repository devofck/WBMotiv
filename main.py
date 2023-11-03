from aiogram import Bot, Dispatcher
from redis.asyncio.client import Redis
from aiogram.fsm.storage.redis import RedisStorage
import asyncio
from handlers.admin.admin_panel import admin_panel
from handlers.background.background import background
from handlers.user.user_panel import user_panel


async def main():
    bot = Bot(
        token='6550734217:AAHmNgorYMK4Lyk9DJaznekD3KMZcgiW1B4',
        disable_web_page_preview=True,
        parse_mode='HTML'
    )
    dp = Dispatcher(
        storage=RedisStorage(Redis())
    )
    dp.resolve_used_update_types()
    dp.include_routers(
        admin_panel,
        user_panel,
        background
    )
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
