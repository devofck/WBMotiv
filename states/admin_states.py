from aiogram.fsm.state import State, StatesGroup


class AddChannel(StatesGroup):
    waiting_for_channel = State()
    wait_for_link = State()


class CreateSending(StatesGroup):
    wait_for_text = State()
    wait_for_media = State()
    wait_for_kb = State()
    confirm = State()