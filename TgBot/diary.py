from aiogram import Router, F
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from aiogram_calendar import SimpleCalendarCallback, SimpleCalendar

import datetime as dt
import logging

from .locale import *
from .callbacks import NavigationCallback
from .utils import *
from .keyboards.diary import *
from .FSM.diary import MarksPeriodForm

from db.models import Account

from ITschool.types import Lesson
from ITschool import learner_client

diary_router = Router()

@diary_router.callback_query(NavigationCallback.filter(F.menu == "main"))
async def main(query: CallbackQuery, state: FSMContext):
    user = await Account(query.from_user.id).get_account()
    await query.message.edit_text(welcome_text(user.first_name), reply_markup=MainMenuKeyboard())
    await state.clear()
    if client_cache.get(query.from_user.id):
        client_cache.pop(query.from_user.id)
    if users_calendar.get(query.from_user.id):
        users_calendar.pop(query.from_user.id)
    if user_cache.get(query.from_user.id):
        user_cache.pop(query.from_user.id)
    
    if final_cache.get(query.from_user.id):
        final_cache.pop(query.from_user.id)

@diary_router.callback_query(NavigationCallback.filter(F.menu == "marks"))
async def marks(query: CallbackQuery):
    if client_cache.get(query.from_user.id):
        client_cache.pop(query.from_user.id)
    if users_calendar.get(query.from_user.id):
        users_calendar.pop(query.from_user.id)
    if user_cache.get(query.from_user.id):
        user_cache.pop(query.from_user.id)
    if final_cache.get(query.from_user.id):
        final_cache.pop(query.from_user.id)
    await query.message.edit_text(marks_main_text, reply_markup=MarksKeyboard())

@diary_router.callback_query(NavigationCallback.filter(F.menu == "marks.week"))
async def marks_week(query: CallbackQuery):
    today = dt.date.today()
    day_of_week = today.weekday()
    date_start = today - dt.timedelta(days=day_of_week)
    date_end = date_start + dt.timedelta(days=6)
    marks = await learner_client.get_period(
        (await Account(query.from_user.id).get_account()).person.id,
        date_start,
        date_end
        )
    marks_text = ""
    for lesson in marks:
        if len(lesson) == 3:
            continue
        marks_text += f"*{validate_text(lesson[0])}*:\n"
        marks_text += ">" + validate_text(" ".join(lesson[1:-2])) + "\r\n"
    if not marks_text:
        marks_text = no_week_marks
    marks_text = marks_text.replace("#goodReason", "").replace("#miss", "")
    await query.message.edit_text(text=marks_week_text + marks_text, parse_mode="Markdownv2", reply_markup=NavigationKeyboard([], back_ref="marks.period"))
    
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
        case _:
            date_start, date_end = period.split(".")
            period_text = f"с {date_start} по {date_end}" 

    date_start, date_end = dt.datetime.strptime(date_start, "%Y-%m-%d"), dt.datetime.strptime(date_end, "%Y-%m-%d")
    await state.set_data({"period": period})
    user_cache = client_cache.get(query.from_user.id, {})
    
    if user_cache.get("period") != period:
        await query.answer("Получаем оценки... ⏳")
        await query.message.edit_text("Получаем оценки... ⏳")
        lessons = await learner_client.get_week(
            (await Account(query.from_user.id).get_account()).person.id,
            date_start,
            date_end
            )
        client_cache[query.from_user.id] = {"period": period, "lessons": lessons}
    else:
        lessons = user_cache["lessons"]
    
    await query.message.edit_text(marks_default_text(period_text), reply_markup=MarksDefaulChoiceLessons(tuple(lessons.keys())))
    
@diary_router.callback_query(NavigationCallback.filter(F.menu == "marks.period.lesson"))
async def watch_marks(query: CallbackQuery, state: FSMContext):
    cntx = await state.get_data()
    subject = cntx.get("subject", NavigationCallback.unpack(query.data).params)
    lessons = client_cache[query.from_user.id]["lessons"]
    
    text = f"Твои оценки по *{validate_text(subject)}*:\n"

    text += ">" + " ".join([validate_text(i.score.mark) for i in lessons.get(subject, [])])
    await state.update_data({"back_ref": "marks.period.lesson"})
    logging.info((await state.get_data())["period"])
    await query.message.edit_text(text, reply_markup=MarksPeriodSortDateButton(back_ref="marks.default" , params=(await state.get_data())["period"]), parse_mode="Markdownv2") #NavigationKeyboard([], back_ref="marks.default", params=(await state.get_data())["period"])
    await state.update_data({"subject": subject})

@diary_router.callback_query(NavigationCallback.filter(F.menu == "marks.period.lesson.date"))
async def watch_marks(query: CallbackQuery, state: FSMContext):
    subject = (await state.get_data())["subject"]
    lessons = client_cache[query.from_user.id]["lessons"]

    last_date = None
    text = f"*Твои оценки по {validate_text(subject)}*:\n"
    for i in lessons[subject]:
        text += f"\n*За {validate_text(i.date.strftime('%d.%m.%Y'))}:*\n" if last_date != i.date else ""
        text += ">" if last_date != i.date else " "
        text += f"{validate_text(i.score.mark)}"
        last_date = i.date

    await query.message.edit_text(text=text, reply_markup=NavigationKeyboard([], "marks.period.lesson", subject), parse_mode="Markdownv2")

@diary_router.callback_query(NavigationCallback.filter(F.menu == "marks.custom"))
async def marks_custom_start(query: CallbackQuery, state: FSMContext):
    users_calendar.update({
        query.from_user.id: SimpleCalendar(locale="ru_RU.UTF-8", show_alerts=True, cancel_btn="Назад ⬅️", today_btn="Сегодня 📍")
    })
    calendar = users_calendar[query.from_user.id]
    calendar.set_dates_range(
        dt.datetime.strptime(learner_client.periods[0]["dateFrom"], "%Y-%m-%d"),
        dt.datetime.today()
        )
    
    await state.set_data({"state": "start_date", "back_ref": "marks.period"})
    await query.message.edit_text("С какого числа хочешь посмотреть оценки?", reply_markup=await calendar.start_calendar())

@diary_router.callback_query(SimpleCalendarCallback.filter(F.act == "CANCEL"))
async def marks_custom_cancel(query: CallbackQuery, state: FSMContext):
    if (await state.get_data()).get("back_ref") == "marks.period":
        await query.message.edit_text(marks_period_text, reply_markup=MarksPeriodChoice())
        await state.clear()
    else:
        await query.message.edit_text("И как ты тут оказался?", reply_markup=NavigationKeyboard(buttons=[], to_main=False))
        await state.clear()

@diary_router.callback_query(NavigationCallback.filter(F.menu == "marks.period.get"))
async def marks_custom_generate(query: CallbackQuery, state: FSMContext):
    date_start = dt.datetime.strptime((await state.get_data())["date_start"], "%Y-%m-%d")
    date_end = dt.datetime.strptime((await state.get_data())["date_end"], "%Y-%m-%d")
    period_text = f"с *{validate_text(date_start.strftime('%d.%m.%Y'))}* по *{validate_text(date_end.strftime('%d.%m.%Y'))}*"
    period = f"{date_start.strftime('%Y-%m-%d')}.{date_end.strftime('%Y-%m-%d')}"

    await state.set_data({"period": period})
    user_cache = client_cache.get(query.from_user.id, {})

    if user_cache.get("period") != period:
        await query.answer("Получаем оценки... ⏳")
        await query.message.edit_text("Получаем оценки... ⏳")
        lessons = await learner_client.get_week(
            (await Account(query.from_user.id).get_account()).person.id,
            date_start,
            date_end
            )
        client_cache[query.from_user.id] = {"period": period, "lessons": lessons}
    else:
        lessons = user_cache["lessons"]
    
    await query.message.edit_text(marks_default_text(period_text), reply_markup=MarksDefaulChoiceLessons(tuple(lessons.keys())), parse_mode="Markdownv2")
    
@diary_router.callback_query(SimpleCalendarCallback.filter(F.act == "DAY"))
async def marks_custom_cancel(query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    calendar: SimpleCalendar = users_calendar[query.from_user.id]
    date = (await calendar.process_day_select(callback_data, query))

    if date[0]:
        date = date[1]
    else:
        logging.info(date)
        return
    data = await state.get_data()
    if not data.get("date_start"):
        calendar.set_dates_range(
            date,
            dt.datetime.today()
        )
        await query.message.edit_text(
            f"Ты выбрал {date.strftime('%d.%m.%Y')}\nПо какое число ты хочешь получить оценки?",
            reply_markup=await calendar.start_calendar()
        )
        await state.update_data({"date_start": date.strftime('%Y-%m-%d')})
    elif not data.get("date_end"):
        await state.update_data({"date_end": date.strftime('%Y-%m-%d')})
        users_calendar.pop(query.from_user.id)
        if data.get("back_ref") == "marks.period":
            date_start = dt.datetime.strftime(dt.datetime.strptime((await state.get_data())["date_start"], "%Y-%m-%d"), "%d.%m.%Y")
            date_end = dt.datetime.strftime(dt.datetime.strptime((await state.get_data())["date_end"], "%Y-%m-%d"), "%d.%m.%Y")
            await query.message.edit_text(confirm_period_text(validate_text(date_start), validate_text(date_end)), reply_markup=PeriodConfirm("marks.period.get", "marks.period"), parse_mode="Markdownv2")

@diary_router.callback_query(SimpleCalendarCallback.filter())
async def marks_choice_second_date(query: CallbackQuery, callback_data: CallbackData):
    calendar = users_calendar[query.from_user.id]
    await calendar.process_selection(query, callback_data)

@diary_router.callback_query(NavigationCallback.filter(F.menu == "marks.final"))
async def marks_final(query: CallbackQuery, state: FSMContext):
    await state.update_data({"back_ref": "marks.final"})
    
    if not (marks:= final_cache.get(query.from_user.id)):
        marks = await learner_client.get_final(
            (await Account(query.from_user.id).get_account()).person.id
        )

    final_cache[query.from_user.id] = marks
    await query.message.edit_text(marks_avg_text, reply_markup=MarksFinalChoice(periods=marks[0][1:]))

@diary_router.callback_query(NavigationCallback.filter(F.menu == "marks.final.period"))
async def marks_final_period(query: CallbackQuery, state: FSMContext):
    period = int(NavigationCallback.unpack(query.data).params)

    marks = final_cache[query.from_user.id]
    period_text = marks[0][period]
    marks_text = f"Итоговые *{period_text}*:\n"

    for subject in marks[1:]:
        if subject[period] == "-":
            continue
        if len(subject[0]) > 23:
            if subject[0].split(".")[0] == "Иностранный язык":
                subject[0] = subject[0].replace("Иностранный язык. ", "")
            elif subject[0].split()[0] == "Основы":
                subject[0] = subject[0].replace("Основы безопасности жизнедеятельности", "ОБЖ")
            else:
                subject[0] = subject[0][:20] + "..."

        marks_text += f"*•* `{validate_text(subject[0])}:{' ' * (35 - 10 - len(subject[0]))}`*{subject[period]}*\n"
        
    if marks_text == f"Итоговые *{period_text}*:\n":
        marks_text = no_final_marks
    back_ref = "marks.final"
    await query.message.edit_text(text=marks_text, parse_mode="Markdownv2", reply_markup=NavigationKeyboard([], back_ref))
    
@diary_router.callback_query(NavigationCallback.filter(F.menu == "marks.avg"))
async def marks_avg(query: CallbackQuery, state: FSMContext):
    await state.update_data({"back_ref": "marks.avg"})
    await query.message.edit_text(marks_avg_text, reply_markup=MarksAvgChoice())

@diary_router.callback_query(NavigationCallback.filter(F.menu == "marks.avg.period"))
async def marks_avg_period(query: CallbackQuery, state: FSMContext):
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
        case _:
            date_start, date_end = period.split(".")
            period_text = f"*с *{validate_text(date_start)}* по *{validate_text(date_end)}*\r*"
    date_start, date_end = dt.datetime.strptime(date_start, "%Y-%m-%d"), dt.datetime.strptime(date_end, "%Y-%m-%d")

    marks = await learner_client.get_period(
        (await Account(query.from_user.id).get_account()).person.id,
        date_start,
        date_end
        )
    marks_text = f"Средние *{period_text}*:\n"

    for lesson in marks:
        if len(lesson) == 3 or lesson[-2].split("#")[0] == "0":
            continue
        if len(lesson[0]) > 23:
            if lesson[0].split(".")[0] == "Иностранный язык":
                lesson[0] = lesson[0].replace("Иностранный язык. ", "")
            elif lesson[0].split()[0] == "Основы":
                lesson[0] = lesson[0].replace("Основы безопасности жизнедеятельности", "ОБЖ")
            else:
                lesson[0] = lesson[0][:20] + "..."

        marks_text += f"*•* `{validate_text(lesson[0])}:{' ' * (35 - 10 - len(lesson[0]))}`*{lesson[-2].split('#')[0]}*\n"
    if not marks_text:
        marks_text = no_period_marks
    back_ref = (await state.get_data())["back_ref"]
    await query.message.edit_text(text=marks_text, parse_mode="Markdownv2", reply_markup=NavigationKeyboard([], back_ref))
