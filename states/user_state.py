from aiogram.fsm.state import State, StatesGroup


class UserSubbed(StatesGroup):
    allow_photo = State()