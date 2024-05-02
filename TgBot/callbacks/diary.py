from aiogram.filters.callback_data import CallbackData


class NavigationCallback(CallbackData, prefix='nav'):
    menu: str
    params: str | None = None
