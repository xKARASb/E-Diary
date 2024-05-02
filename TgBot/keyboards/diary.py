from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from TgBot.callbacks import NavigationCallback

def MainMenuKeyboard():
    buttons = [
        [
            InlineKeyboardButton(text="Задания 📝", callback_data=NavigationCallback(menu="home_task").pack()),
            InlineKeyboardButton(text="Расписание 📃", callback_data=NavigationCallback(menu="timetable").pack())
        ],
        [
            InlineKeyboardButton(text="Оценки 🫡", callback_data=NavigationCallback(menu="marks").pack())
        ]
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def NavigationKeyboard(buttons: list, back_ref: str, params = None, to_main=True):
    button = [
            InlineKeyboardButton(text="Назад 🔙", callback_data=NavigationCallback(menu=back_ref, params=params).pack()),
            ]
    if to_main:
        button.append(InlineKeyboardButton(text="Главное меню 📍", callback_data=NavigationCallback(menu="main").pack()))

    buttons.append(button)
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def MarksKeyboard():
    buttons = [
        [
            InlineKeyboardButton(text="За неделю", callback_data=NavigationCallback(menu="marks.week").pack()),
            InlineKeyboardButton(text="Период", callback_data=NavigationCallback(menu="marks.period").pack())
        ],
        [
            InlineKeyboardButton(text="Итоговые", callback_data=NavigationCallback(menu="marks.final").pack()),
        ]
    ]
    return NavigationKeyboard(buttons, "main", to_main=False)

def MarksPeriodChoice():
    buttons = [
        [
            InlineKeyboardButton(text="I", callback_data=NavigationCallback(menu="marks.default", params="quoter.first").pack()),
            InlineKeyboardButton(text="II", callback_data=NavigationCallback(menu="marks.default", params="quoter.second").pack()),
            InlineKeyboardButton(text="III", callback_data=NavigationCallback(menu="marks.default", params="quoter.third").pack()),
            InlineKeyboardButton(text="IV", callback_data=NavigationCallback(menu="marks.default", params="quoter.fourth").pack())
        ],
        [
            InlineKeyboardButton(text="I половина", callback_data=NavigationCallback(menu="marks.default", params="half.first").pack()),
            InlineKeyboardButton(text="II половина", callback_data=NavigationCallback(menu="marks.default", params="half.second").pack()),
        ],
        [
            InlineKeyboardButton(text="Выбрать период", callback_data=NavigationCallback(menu="marks.custom").pack()),
        ]
    ]
    return NavigationKeyboard(buttons, "marks")

def MarksDefaulChoiceLessons(lessons):
    buttons = [
        [
            InlineKeyboardButton(text=lessons[i], callback_data=NavigationCallback(menu="marks.default.lesson", params=f"{lessons[i]}").pack()),
            InlineKeyboardButton(text=lessons[i+1], callback_data=NavigationCallback(menu="marks.default.lesson", params=f"{lessons[i+1]}").pack()),
        ]
        for i in range(0, len(lessons)-1, 2)
    ]

    if len(lessons) % 2 != 0:
        buttons.append(
            [
                InlineKeyboardButton(text=lessons[-1], callback_data=NavigationCallback(menu="marks.default.lesson", params=f"{lessons[-1]}").pack()),
            ]
        )

    return NavigationKeyboard(buttons, "marks.period")

def MarksPeriodDateButton(params):
    buttons = [
        [
            InlineKeyboardButton(text="Отсортировать по дате", callback_data=NavigationCallback(menu="marks.default.lesson.date").pack()),
        ]
    ]
    return NavigationKeyboard(buttons, back_ref="marks.default", params=params)