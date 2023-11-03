import os

from aiogram.types import InlineKeyboardMarkup
from aiogram import F, Bot, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InputFile
from aiogram.types.input_file import FSInputFile
from aiogram.fsm.context import FSMContext
from filters.is_admin import IsAdmin
from keyboard import keyboard
from states.admin_states import AddChannel, CreateSending
from aiogram.exceptions import TelegramBadRequest
from database.db import Database
import matplotlib.pyplot as plt
import asyncio


global last_kb

admin_panel = Router()


@admin_panel.message(IsAdmin(), Command('admin'))
async def admin_entrance(m: Message):
    await m.answer(
        "<b>Вы вошли в панель администратора!</b>\n"
        "Воспользуйтесь клавиатурой ниже",
        reply_markup=keyboard.admin_kb()
    )


@admin_panel.message(IsAdmin(), F.text == '🎯 Обязательные подписки')
async def channel_management_menu(m: Message):
    await m.answer(
        '<b>Панель управления обязательными подписками</b>',
        reply_markup=keyboard.channel_management_kb()
    )


@admin_panel.callback_query(IsAdmin(), F.data == 'delete_channel')
async def delete_channel(c: CallbackQuery):
    db = Database()
    channels = db.get_channels()
    await c.message.edit_text(
        '<b>Выберите канал для удаления из ОП</b>',
        reply_markup=keyboard.channels_to_del_kb(channels)
    )


@admin_panel.callback_query(IsAdmin(), F.data.startswith("confirm_delete_channel"))
async def delete_channel_confirmed(c: CallbackQuery):
    channel_id = c.data.split(':')[1]
    db = Database()
    db.delete_channel(channel_id)
    channels = db.get_channels()
    await c.message.edit_reply_markup(
        reply_markup=keyboard.channels_to_del_kb(channels)
    )


@admin_panel.callback_query(IsAdmin(), F.data == 'add_new_channel')
async def choice_channel(c: CallbackQuery, state: FSMContext):
    await c.message.answer(
        '<b>Выберите канал, пользуясь кнопкой ниже</b>',
        reply_markup=keyboard.send_channel_kb()
    )
    await state.set_state(
        AddChannel.waiting_for_channel
    )


@admin_panel.message(IsAdmin(), AddChannel.waiting_for_channel, F.chat_shared)
async def add_channel(m: Message, bot: Bot, state: FSMContext):
    try:
        chat_data = await bot.get_chat(
            chat_id=m.chat_shared.chat_id
        )
    except TelegramBadRequest:
        await m.answer(
            '<b>В данный момент бот не является администратором канала!</b>\n\n'
            'Дайте боту права и повторите попытку.'
        )
        return
    db = Database()
    if not db.get_channel(channel_id=chat_data.id):
        await m.answer(
            'Ошибка! Этот канал уже добавлен!\n\n'
            'Наверное, вы перетрудились, заварите кофейку 😊☕️'
        )
        return

    await m.answer('<b>Почти! Теперь осталось прислать ссылку!</b>', reply_markup=keyboard.admin_kb())
    await state.update_data(
        channel_id=chat_data.id,
        channel_title=chat_data.title
    )
    await state.set_state(
        AddChannel.wait_for_link
    )


@admin_panel.message(AddChannel.wait_for_link)
async def process_new_channel(m: Message, state: FSMContext):
    if 't.me/' not in m.text:
        await m.answer(
            '<b>Пришлите ссылку на канал, а не это)</b>'
        )
        return
    db = Database()
    data = await state.get_data()
    db.add_channel(
        channel_id=data['channel_id'],
        title=data['channel_title'],
        link=m.text
    )
    await m.answer(
        '<b>✅ Канал успешно добавлен!</b>'
    )
    await state.clear()


@admin_panel.message(IsAdmin(), F.text == "📊 Статистика")
async def get_stat(m: Message):
    db = Database()
    stat = db.get_stat()

    vals = [stat[0][0], stat[0][1]]
    labels = ['Живы', 'Заблокировали']
    fig, ax = plt.subplots()
    ax.pie(vals, labels=labels, wedgeprops=dict(width=0.5))
    plt.title('Соотношение живых и мертвых пользователей')
    plt.savefig('temp/stat.png')
    await m.answer_photo(
        photo=FSInputFile(
            path='temp/stat.png'
        ),
        caption=f'<b>📊 Статистика бота</b>\n\n'
        f'Пользователей в боте:\n'
        f'➖ Всего: {stat[0][0]}\n'
        f'➖ Живых: {stat[0][0] - stat[0][1]}\n'
        f'➖ Заблокированных: {stat[0][1]}\n\n'
        f'Подписка на обязательные каналы:\n'
        f'➖ {stat[1][0]}\n'
        f'Зашло в бот:\n'
        f'➖ Сегодня: {stat[0][2][0]}\n'
        f'➖ За 48 часов: {stat[0][2][1]}\n'
        f'➖ За неделю: {stat[0][2][2]}\n'
        f'➖ За месяц: {stat[0][2][3]}',
        reply_markup=keyboard.deploy_botstat()
    )
    os.remove('temp/stat.png')


@admin_panel.callback_query(F.data == 'deploy_botstat')
async def deploy_botstat(c: CallbackQuery):
    db = Database()
    deploy = open('temp/botstat.txt', 'w')
    text = ''
    for user in db.get_alive():
        text += str(user[1]) + '\n'
    deploy.write(text)
    deploy.close()
    await c.message.answer_document(
        document=FSInputFile(
            path='temp/botstat.txt'
        )
    )


@admin_panel.message(F.text == "📩 Рассылка")
async def mailing(m: Message, state: FSMContext):
    await m.answer(
        'Пришлите текст для рассылки!'
    )
    await state.set_state(
        CreateSending.wait_for_text
    )


@admin_panel.message(CreateSending.wait_for_text)
async def confirm_post(m: Message, state: FSMContext):
    await m.copy_to(chat_id=m.from_user.id, reply_markup=m.reply_markup)
    await m.answer('<b>Вот так ваш пост увидят получатели</b>\n\n'
                   'Отправляем?',
                   reply_markup=keyboard.confirm_sending_kb()
                   )
    await state.update_data(
        msg_id=m.message_id,
    )
    global last_kb
    if m.reply_markup:
        last_kb = m.reply_markup
    else:
        last_kb = None

    await state.set_state(CreateSending.confirm)


@admin_panel.callback_query(CreateSending.confirm, F.data == 'confirm_no')
async def decline_post(c: CallbackQuery, state: FSMContext):
    await c.message.edit_text('❌ Рассылка отменена')
    await state.clear()


@admin_panel.callback_query(CreateSending.confirm, F.data == 'confirm_yes')
async def accept_post(c: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    await c.message.edit_text('✅ Рассылка началась')
    db = Database()
    count = 0
    global last_kb
    for user in db.get_alive():
        try:
            await bot.copy_message(
                chat_id=user[1],
                from_chat_id=c.from_user.id,
                message_id=data['msg_id'],
                reply_markup=last_kb
            )
            count += 1
            await asyncio.sleep(0.1)
        except:
            pass
    await c.message.answer(
        '<b>💎 Рассылка окончена</b>\n\n'
        f'Сообщений успешно отправлено: {count}'
    )
    last_kb = None
