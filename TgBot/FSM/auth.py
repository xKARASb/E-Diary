from aiogram.fsm.state import StatesGroup, State

class AuthForm(StatesGroup):
    name = State()
    last_name = State()
    verification = State()
    course = State()
    letter = State()
    confirm = State()