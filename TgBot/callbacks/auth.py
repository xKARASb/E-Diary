from aiogram.filters.callback_data import CallbackData

class AuthCallback(CallbackData, prefix='auth'):
    action: str