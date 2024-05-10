from aiogram import Router, F
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, CallbackQuery, LinkPreviewOptions
from aiogram.fsm.context import FSMContext

from .callbacks import NavigationCallback
from .keyboards.timetable import *
from .utils import validate_text, user_cache


import logging
import datetime as dt

from db.models import Account
from ITschool import learner_client
from ITschool.types import Lesson

timetable_router = Router()

@timetable_router.callback_query(NavigationCallback.filter(F.menu == "timetable"))
async def timetable(query: CallbackQuery, state: FSMContext):
    today = dt.date.today()
    day_of_week = today.weekday()
    date_start = today - dt.timedelta(days=day_of_week)
    date_end = date_start + dt.timedelta(days=6)

    await state.update_data(date_start=date_start.strftime("%Y-%m-%d"))

    person_id = await Account(query.from_user.id).get_person_id()

    await query.answer("Получаем расписание...")
    lessons = await learner_client.get_week(person_id, date_start, date_end, sort_by="date")
    user_cache.update({query.from_user.id: {date_start.strftime("%Y-%m-%d"): lessons}})

    return query.message.edit_text(text="Расписание на какой день?", reply_markup=TimeTableChoiceDay(tuple(lessons.keys()), week_start=date_start, week_end=date_end))

@timetable_router.callback_query(NavigationCallback.filter(F.menu == "timetable.week.prev"))
async def timetable_week_prev(query: CallbackQuery, state: FSMContext):
    date_start = dt.datetime.strptime((await state.get_data())["date_start"], "%Y-%m-%d") - dt.timedelta(days=7)
    date_end = date_start + dt.timedelta(days=6)
    
    await state.update_data(date_start=date_start.strftime("%Y-%m-%d"))

    if not (lessons := user_cache.get(query.from_user.id, {}).get(date_start.strftime("%Y-%m-%d"), False)):
        await query.answer("Получаем расписание...")
        person_id = await Account(query.from_user.id).get_person_id()
        lessons = await learner_client.get_week(person_id, date_start, date_end, sort_by="date")
        user_cache[query.from_user.id].update({date_start.strftime("%Y-%m-%d"): lessons})
    
    await query.message.edit_reply_markup(reply_markup=TimeTableChoiceDay(tuple(lessons.keys()), week_start=date_start, week_end=date_end, next=True))

@timetable_router.callback_query(NavigationCallback.filter(F.menu == "timetable.week.next"))
async def timetable_week_next(query: CallbackQuery, state: FSMContext):
    date_start = dt.datetime.strptime((await state.get_data())["date_start"], "%Y-%m-%d") + dt.timedelta(days=7)
    date_end = date_start + dt.timedelta(days=6)

    await state.update_data(date_start=date_start.strftime("%Y-%m-%d"))

    if not (lessons := user_cache.get(query.from_user.id, {}).get(date_start.strftime("%Y-%m-%d"), False)):
        await query.answer("Получаем расписание...")
        person_id = await Account(query.from_user.id).get_person_id()
        lessons = await learner_client.get_week(person_id, date_start, date_end, sort_by="date")
        user_cache[query.from_user.id].update({date_start.strftime("%Y-%m-%d"): lessons})
    
    next = True
    if date_end > dt.datetime.today():
        next = False
    
    await query.message.edit_reply_markup(reply_markup=TimeTableChoiceDay(tuple(lessons.keys()), week_start=date_start, week_end=date_end, next=next))

@timetable_router.callback_query(NavigationCallback.filter(F.menu == "timetable.week.default"))
async def timetable_week_next(query: CallbackQuery):
    await query.answer()

@timetable_router.callback_query(NavigationCallback.filter(F.menu == "timetable.week.current"))
async def timetable_week_next(query: CallbackQuery, state: FSMContext):
    date_start = dt.datetime.strptime((await state.get_data())["date_start"], "%Y-%m-%d")
    date_end = date_start + dt.timedelta(days=6)

    await state.update_data(date_start=date_start.strftime("%Y-%m-%d"))

    if not (lessons := user_cache.get(query.from_user.id, {}).get(date_start.strftime("%Y-%m-%d"), False)):
        await query.answer("Получаем расписание...")
        person_id = await Account(query.from_user.id).get_person_id()
        lessons = await learner_client.get_week(person_id, date_start, date_end, sort_by="date")
        user_cache[query.from_user.id].update({date_start.strftime("%Y-%m-%d"): lessons})
    
    next = True
    if date_end > dt.datetime.today():
        next = False

    await query.message.edit_text(text="Расписание на какой день?", reply_markup=TimeTableChoiceDay(tuple(lessons.keys()), week_start=date_start, week_end=date_end, next=next))


@timetable_router.callback_query(NavigationCallback.filter(F.menu == "timetable.day"))
async def timetable_day(query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    week_start = (await state.get_data())["date_start"]
    day_date = callback_data.params # dt.datetime.strptime(callback_data.params, "%Y-%m-%d")
    day_date_dt = dt.datetime.strptime(callback_data.params, "%Y-%m-%d")
    lessons = user_cache[query.from_user.id].get(week_start, {}).get(day_date, [])
    
    i: Lesson
    text = f"Расписание на *{day_date_dt.strftime('%A')}*, {validate_text(day_date_dt.strftime('%d.%m'))}:"
    for i in lessons:
        text += f"\n{i.lesson_shift.num}\. *{validate_text(i.subject_short_name)}*"
        text += f" _{i.lesson_shift.start_time.strftime('%H:%M')} \- {i.lesson_shift.end_time.strftime('%H:%M')}_"
        i.home_task = i.home_task if i.home_task else "ДЗ не указано"
        for task in i.home_task.split("\n"):
            text += f"\n>{validate_text(task)}"

    await query.message.edit_text(text=text, reply_markup=NavigationKeyboard([], "timetable.week.current", to_main=True), parse_mode="Markdownv2", disable_web_page_preview=True)