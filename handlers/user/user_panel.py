from aiogram import F, Bot, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from keyboard import keyboard
from database.db import Database
import asyncio
from states.user_state import UserSubbed


user_panel = Router()


@user_panel.message(CommandStart())
async def user_entrance(m: Message, bot: Bot):
    db = Database()
    db.reg_user(m.from_user.id)

    db = Database()
    channels = db.get_channels()
    count = 0
    for channel in channels:
        user = await bot.get_chat_member(
            chat_id=channel[2],
            user_id=m.from_user.id
        )
        if user.status != 'left' or db.is_requested(channel[2], m.from_user.id):
            count += 1

    if len(channels) != count:
        await m.answer(
            '<b>🤚 Привет!</b> Наш бот <b>полностью бесплатен!</b>\n\n'
            'Но для его работы, нужно подписаться на каналы ниже 👇',
            reply_markup=keyboard.channel_sub_link(channels)
        )
        return
    await m.answer(
        'Пришлите фото, видео или текстовый запрос и <b>я найду нужный товар '
        'среди сотен тысяч других!</b>'
    )


@user_panel.callback_query(F.data == 'check_sub')
async def process_check_subscribe(c: CallbackQuery, bot: Bot, state: FSMContext):
    db = Database()
    channels = db.get_channels()
    count = 0
    for channel in channels:
        user = await bot.get_chat_member(
            chat_id=channel[2],
            user_id=c.from_user.id
        )
        if user.status != 'left' or db.is_requested(channel[2], c.from_user.id):
            count += 1

    if len(channels) != count:
        await c.answer(
            '❌ Вы не подписались на все каналы!',
            show_alert=True
        )
        return
    await c.message.answer(
        "💎 Доступ к боту открыт! "
        "<b>Теперь отправьте фото, текст или видео "
        "(опишите вещь, которую хотите найти)</b>"
    )
    db.increase_subs(channels)
    await state.set_state(
        UserSubbed.allow_photo
    )


@user_panel.message(UserSubbed.allow_photo)
async def process_photo(m: Message, bot: Bot):

    msg = await m.answer('🔍 Идет поиск')
    for i in range(3):
        await msg.edit_text(
            text='🔎 Идет поиск'
        )
        await asyncio.sleep(0.5)
        await msg.edit_text(
            text='🔍 Идет поиск'
        )
        await asyncio.sleep(0.5)

    await msg.edit_text(
        text='<b>✅ Ваш запрос на поиск принят на обработку.</b>\n\n'
             'В связи с повышенной нагрузкой, ответ придёт в течение 24-48 часов, ожидайте! 🤗'
    )
