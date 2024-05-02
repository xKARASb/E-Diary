from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import datetime as dt
import logging

from .locale import *
from .callbacks import NavigationCallback
from .keyboards.diary import *
from .FSM.diary import MarksPeriodForm


from db.models import Account

from ITschool.types import Lesson
from ITschool import learner_client

diary_router = Router()

client_cache = {}

def validate_text(text, exct = []):
    validate_text = []
    varity = set(('_', '*', '[', ']', '(', ')', '~', '`', '#', '+', '-', '=', '|', '{', '}', '.', '!', ">", "\\"))
    varity -= set(exct)
    for char in text:
        if char in varity:
            validate_text.append("\\")
        validate_text.append(char)
    return "".join(validate_text)

@diary_router.callback_query(NavigationCallback.filter(F.menu == "main"))
async def main(query: CallbackQuery, state: FSMContext):
    user = await Account(query.from_user.id).get_account()
    await query.message.edit_text(welcome_text(user.learner.first_name), reply_markup=MainMenuKeyboard())
    await state.clear()
    if client_cache.get(query.from_user.id):
        client_cache.pop(query.from_user.id)
    # await query.message.answer(welcome_text(user.learner.first_name), reply_markup=MainMenuKeyboard())
    # await query.message.delete()

@diary_router.callback_query(NavigationCallback.filter(F.menu == "home_task"))
async def home_task(query: CallbackQuery):
    await query.answer("В разработке... ⏳")

@diary_router.callback_query(NavigationCallback.filter(F.menu == "timetable"))
async def timetable(query: CallbackQuery):
    await query.answer("В разработке... ⏳")

@diary_router.callback_query(NavigationCallback.filter(F.menu == "marks"))
async def marks(query: CallbackQuery):
    await query.message.edit_text(marks_main_text, reply_markup=MarksKeyboard())

@diary_router.callback_query(NavigationCallback.filter(F.menu == "marks.week"))
async def marks_week(query: CallbackQuery):
    today = dt.date.today()
    day_of_week = today.weekday()
    date_start = today - dt.timedelta(days=day_of_week) - dt.timedelta(days=14)
    date_end = date_start + dt.timedelta(days=6) - dt.timedelta(days=14)
    marks = await learner_client.get_period(
        (await Account(query.from_user.id).get_account()).learner.person_id,
        date_start,
        date_end
        )
    marks_text = ""
    for lesson in marks:
        if len(lesson) == 3:
            continue
        marks_text += f"{validate_text(lesson[0])}*:\n"
        marks_text += ">" + validate_text(" ".join(lesson[1:-2])) + "\r\n"
    if not marks_text:
        marks_text = no_week_marks
    marks_text = marks_text.replace("#goodReason", "").replace("#miss", "")
    await query.message.edit_text(text=marks_week_text + marks_text, parse_mode="Markdownv2", reply_markup=NavigationKeyboard([], back_ref="marks"))
    # await query.message.delete()

@diary_router.callback_query(NavigationCallback.filter(F.menu == "marks.period"))
async def marks_week(query: CallbackQuery):
    await query.message.edit_text(marks_period_text, reply_markup=MarksPeriodChoice())  


@diary_router.callback_query(NavigationCallback.filter(F.menu == "marks.default"))
async def marks_default(query: CallbackQuery, state: FSMContext):
    period = NavigationCallback.unpack(query.data).params
    period_text = None
    match period:
        case "quoter.first":
            date_start = learner_client.periods[0]["dateFrom"]
            date_end = learner_client.periods[0]["dateTo"]
            period_text = "I четверть"
        case "quoter.second":
            date_start = learner_client.periods[1]["dateFrom"]
            date_end = learner_client.periods[1]["dateTo"]
            period_text = "II четверть"
        case "quoter.third":
            date_start = learner_client.periods[2]["dateFrom"]
            date_end = learner_client.periods[2]["dateTo"]
            period_text = "III четверть"
        case "quoter.fourth":
            date_start = learner_client.periods[3]["dateFrom"]
            date_end = learner_client.periods[3]["dateTo"]
            period_text = "IV четверть"
        case "half.first":
            date_start = learner_client.periods[0]["dateFrom"]
            date_end = learner_client.periods[1]["dateTo"]
            period_text = "I полугодие"
        case "half.second":
            date_start = learner_client.periods[2]["dateFrom"]
            date_end = learner_client.periods[3]["dateTo"]
            period_text = "II полугодие"

    date_start, date_end = dt.datetime.strptime(date_start, "%Y-%m-%d"), dt.datetime.strptime(date_end, "%Y-%m-%d")
    await state.set_data({"period": period})
    user_cache = client_cache.get(query.from_user.id, {})
    
    if user_cache.get("period") != period:
        await query.answer("Получаем оценки... ⏳")
        await query.message.edit_text("Получаем оценки... ⏳")
        lessons = await learner_client.get_week((await Account(query.from_user.id).get_account()).learner.person_id, date_start, date_end)
        client_cache[query.from_user.id] = {"period": period, "lessons": lessons}
    else:
        lessons = user_cache["lessons"]

    await query.message.edit_text(f"{period_text}\n Выбери интересующий урок", reply_markup=MarksDefaulChoiceLessons(tuple(lessons.keys())))
    
@diary_router.callback_query(NavigationCallback.filter(F.menu == "marks.default.lesson"))
async def watch_marks(query: CallbackQuery, state: FSMContext):
    subject = NavigationCallback.unpack(query.data).params
    lessons = client_cache[query.from_user.id]["lessons"]
    
    text = f"*Твои оценки по {validate_text(subject)}*:\n"

    text += ">" + " ".join([validate_text(i.score.mark) for i in lessons.get(subject, [])])
    print(await state.get_data())
    await query.message.edit_text(text, reply_markup=MarksPeriodDateButton(params=(await state.get_data())["period"]), parse_mode="Markdownv2") #NavigationKeyboard([], back_ref="marks.default", params=(await state.get_data())["period"])
    await state.update_data({"subject": subject})

@diary_router.callback_query(NavigationCallback.filter(F.menu == "marks.default.lesson.date"))
async def watch_marks(query: CallbackQuery, state: FSMContext):
    subject = (await state.get_data())["subject"]
    lessons = client_cache[query.from_user.id]["lessons"]

    last_date = None
    text = f"*Твои оценки по {validate_text(subject)}*:\n"
    for i in lessons[subject]:
        text += f"\n*За {validate_text(i.date.strftime('%d.%m.%Y'))}:*\n" if last_date!= i.date else ""
        text += ">" if last_date != i.date else " "
        text += f"{validate_text(i.score.mark)}"
        last_date = i.date

    await query.message.edit_text(text=text, reply_markup=NavigationKeyboard([], "marks.default.lesson", subject), parse_mode="Markdownv2")

@diary_router.callback_query(NavigationCallback.filter(F.menu == "marks.custom"))
async def marks_custom(query: CallbackQuery):
    await query.answer("В разработке... ⏳")

@diary_router.callback_query(NavigationCallback.filter(F.menu == "marks.final"))
async def marks_week(query: CallbackQuery):
    await query.answer("В разработке... ⏳")
