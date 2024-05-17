from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from TgBot.callbacks import NavigationCallback

def MainMenuKeyboard():
    buttons = [
        [
            InlineKeyboardButton(text="Оценки 🫡", callback_data=NavigationCallback(menu="marks").pack()), 
            InlineKeyboardButton(text="Расписание 📃", callback_data=NavigationCallback(menu="timetable").pack())
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def NavigationKeyboard(buttons: list = [], back_ref: str = "main", params = None, to_main=True):
    button = [
            InlineKeyboardButton(text="Назад ⬅️", callback_data=NavigationCallback(menu=back_ref, params=params).pack()),
            ]
    if to_main:
        button.append(InlineKeyboardButton(text="Главное меню 📍", callback_data=NavigationCallback(menu="main").pack()))

    buttons.append(button)
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def MarksKeyboard():
    buttons = [
        [
            InlineKeyboardButton(text="Средние оценки 📊", callback_data=NavigationCallback(menu="marks.avg").pack()),
            InlineKeyboardButton(text="Все оценки ⚡", callback_data=NavigationCallback(menu="marks.period").pack())
        ],
        [
            InlineKeyboardButton(text="Итоговые 💌", callback_data=NavigationCallback(menu="marks.final").pack()),
        ]
    ]
    return NavigationKeyboard(buttons, "main", to_main=False)

def MarksPeriodChoice(menu = "marks.default"):
    buttons = [
        [
            InlineKeyboardButton(text="Неделя", callback_data=NavigationCallback(menu="marks.week").pack()),
            
        ],
        [
            InlineKeyboardButton(text="I", callback_data=NavigationCallback(menu=menu, params="quoter.first").pack()),
            InlineKeyboardButton(text="II", callback_data=NavigationCallback(menu=menu, params="quoter.second").pack()),
            InlineKeyboardButton(text="III", callback_data=NavigationCallback(menu=menu, params="quoter.third").pack()),
            InlineKeyboardButton(text="IV", callback_data=NavigationCallback(menu=menu, params="quoter.fourth").pack())
        ],
        [
            InlineKeyboardButton(text="I полугодие", callback_data=NavigationCallback(menu=menu, params="half.first").pack()),
            InlineKeyboardButton(text="II полугодие", callback_data=NavigationCallback(menu=menu, params="half.second").pack()),
        ],
        [
            InlineKeyboardButton(text="Выбрать период 🗓️", callback_data=NavigationCallback(menu="marks.custom").pack()),
        ]
    ]
    return NavigationKeyboard(buttons, "marks")

def MarksAvgChoice(menu = "marks.avg.period", periods = []):
    buttons = [
        [
            InlineKeyboardButton(text="I", callback_data=NavigationCallback(menu=menu, params="quoter.first").pack()),
            InlineKeyboardButton(text="II", callback_data=NavigationCallback(menu=menu, params="quoter.second").pack()),
            InlineKeyboardButton(text="III", callback_data=NavigationCallback(menu=menu, params="quoter.third").pack()),
            InlineKeyboardButton(text="IV", callback_data=NavigationCallback(menu=menu, params="quoter.fourth").pack())
        ],
        [
            InlineKeyboardButton(text="I полугодие", callback_data=NavigationCallback(menu=menu, params="half.first").pack()),
            InlineKeyboardButton(text="II полугодие", callback_data=NavigationCallback(menu=menu, params="half.second").pack()),
        ],
    ]
    return NavigationKeyboard(buttons, "marks")

def MarksFinalChoice(menu = "marks.final.period", periods = []):
    buttons = [
        [
            InlineKeyboardButton(text=periods[i], callback_data=NavigationCallback(menu=menu, params=i+1).pack()),
            InlineKeyboardButton(text=periods[i+1], callback_data=NavigationCallback(menu=menu, params=i+2).pack())
        ]        
        for i in range(0, len(periods)-1, 2)
    ]
    
    if len(periods) % 2 == 1:
        buttons.append(
            [
                InlineKeyboardButton(text=periods[-1], callback_data=NavigationCallback(menu=menu, params=-1).pack()),
            ]
        )
    return NavigationKeyboard(buttons, "marks")

def MarksDefaulChoiceLessons(lessons):
    buttons = [
        [
            InlineKeyboardButton(text=lessons[i], callback_data=NavigationCallback(menu="marks.period.lesson", params=f"{lessons[i]}").pack()),
            InlineKeyboardButton(text=lessons[i+1], callback_data=NavigationCallback(menu="marks.period.lesson", params=f"{lessons[i+1]}").pack()),
        ]
        for i in range(0, len(lessons)-1, 2)
    ]

    if len(lessons) % 2 == 1:
        buttons.append(
            [
                InlineKeyboardButton(text=lessons[-1], callback_data=NavigationCallback(menu="marks.period.lesson", params=f"{lessons[-1]}").pack()),
            ]
        )

    return NavigationKeyboard(buttons, "marks.period")

def MarksPeriodSortDateButton(back_ref, params):
    buttons = [
        [
            InlineKeyboardButton(text="Показать даты 📅", callback_data=NavigationCallback(menu="marks.period.lesson.date").pack()),
            InlineKeyboardButton(text="Средние оценки 📊", callback_data=NavigationCallback(menu="marks.avg.period", params=params).pack())
        ]
    ]
    return NavigationKeyboard(buttons, back_ref=back_ref, params=params)

def PeriodConfirm(menu, back_ref):
    buttons = [
        [
            InlineKeyboardButton(text="❌", callback_data=NavigationCallback(menu=back_ref).pack()),
            InlineKeyboardButton(text="✅", callback_data=NavigationCallback(menu=menu).pack()),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)