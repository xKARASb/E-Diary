from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from TgBot.callbacks import NavigationCallback

from datetime import datetime as dt
from locale import setlocale, LC_TIME

from .diary import NavigationKeyboard

setlocale(LC_TIME, "ru_RU.UTF-8")

def TimeTableChoiceDay(dates, next=False, week_start=None, week_end=None):
    buttons = [
        [
            InlineKeyboardButton(text="<", callback_data=NavigationCallback(menu="timetable.week.prev").pack()),
            InlineKeyboardButton(text=f"{week_start.strftime('%d.%m')}", callback_data=NavigationCallback(menu="timetable.week.default").pack()),
            InlineKeyboardButton(text=f"по", callback_data=NavigationCallback(menu="timetable.week.default").pack()),
            InlineKeyboardButton(text=f"{week_end.strftime('%d.%m')}", callback_data=NavigationCallback(menu="timetable.week.default").pack()),
            InlineKeyboardButton(text=f" ", callback_data=NavigationCallback(menu="timetable.week.default").pack()),

        ]
    ]

    if next:
        buttons[0][4] = InlineKeyboardButton(text=">", callback_data=NavigationCallback(menu="timetable.week.next").pack())

    buttons += [
        [
            InlineKeyboardButton(text=dt.strptime(dates[i], '%Y-%m-%d').strftime('%A'), callback_data=NavigationCallback(menu="timetable.day", params=dates[i]).pack()),
            InlineKeyboardButton(text=dt.strptime(dates[i+1], '%Y-%m-%d').strftime('%A'), callback_data=NavigationCallback(menu="timetable.day", params=dates[i+1]).pack()),
        ]
        for i in range(0, len(dates)-1, 2)
    ]

    if len(dates) % 2 == 1:
        buttons.append(
            [
                InlineKeyboardButton(text=dt.strptime(dates[-1], '%Y-%m-%d').strftime('%A'), callback_data=NavigationCallback(menu="timetable.day", params=dates[-1]).pack()),
            ]
        )
    return NavigationKeyboard(buttons, to_main=False)

