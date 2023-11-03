from aiogram.utils.keyboard import ReplyKeyboardMarkup, InlineKeyboardBuilder, InlineKeyboardButton, \
    ReplyKeyboardBuilder, KeyboardButton
from aiogram.types import KeyboardButtonRequestChat


def admin_kb():
    kb = [
        [
            KeyboardButton(text="📊 Статистика"),
            KeyboardButton(text="📩 Рассылка")
        ],
        [KeyboardButton(text='🎯 Обязательные подписки')]
    ]

    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def channel_management_kb():
    kb = InlineKeyboardBuilder()
    kb.add(
        InlineKeyboardButton(text='✅ Добавить канал', callback_data='add_new_channel')
    ).row(
        InlineKeyboardButton(text='❌ Удалить канал', callback_data='delete_channel')
    )
    return kb.as_markup()


def send_channel_kb():
    kb = ReplyKeyboardBuilder()

    kb.add(
        KeyboardButton(
            request_chat=KeyboardButtonRequestChat(
                chat_is_channel=True,
                request_id=1,
            ),
            text='Выбрать канал',
        )
    )
    return kb.as_markup(resize_keyboard=True)


def channel_sub_link(channels: list[list]):
    kb = InlineKeyboardBuilder()
    for channel in channels:
        kb.row(
            InlineKeyboardButton(text=channel[1], url=channel[4])
        )
    if channels:
        kb.row(
            InlineKeyboardButton(text='✅ Я подписался', callback_data='check_sub')
        )
    return kb.as_markup()


def deploy_botstat():
    kb = InlineKeyboardBuilder()
    kb.add(
        InlineKeyboardButton(text='📈 Выгрузить для BotStat', callback_data='deploy_botstat')
    )
    return kb.as_markup()


def confirm_sending_kb():
    kb = InlineKeyboardBuilder()
    kb.add(
        InlineKeyboardButton(text='✅ Да', callback_data='confirm_yes'),
        InlineKeyboardButton(text='❌ Нет', callback_data='confirm_no')
    )
    return kb.as_markup()


def channels_to_del_kb(channels):
    kb = InlineKeyboardBuilder()
    for channel in channels:
        kb.row(
            InlineKeyboardButton(
                text=channel[1],
                callback_data="confirm_delete_channel:" + str(channel[2])
            )
        )
    return kb.as_markup()
