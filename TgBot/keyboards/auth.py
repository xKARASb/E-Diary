from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from TgBot.callbacks import AuthCallback, NavigationCallback


def AuthKeyboard():
    buttons = [
        [InlineKeyboardButton(text="Авторизоваться 🪪", callback_data=AuthCallback(action="start").pack())],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def PersonalDataKeyboard():
    buttons = [
        [
            InlineKeyboardButton(text="Отмена 🚫", callback_data=AuthCallback(action="cancel").pack()),
            InlineKeyboardButton(text="Разрешить ✅", callback_data=AuthCallback(action="allow").pack())
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def ConfirmUserKeyboard():
    buttons = [
        [
            InlineKeyboardButton(text="Нет ❌", callback_data=AuthCallback(action="deny").pack()),
            InlineKeyboardButton(text="Да ✅", callback_data=AuthCallback(action="confirm").pack())
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def ToMainMenuKeyboard():
    buttons = [
        [InlineKeyboardButton(text="Главное меню 📍", callback_data=NavigationCallback(menu="main").pack())]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)