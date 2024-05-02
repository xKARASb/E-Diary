from aiogram.fsm.state import StatesGroup, State

class MarksPeriodForm(StatesGroup):
    period = State()
    subject = State()
