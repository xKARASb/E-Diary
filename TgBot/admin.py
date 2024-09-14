from aiogram import Router, F
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from aiogram_calendar import SimpleCalendarCallback, SimpleCalendar

import datetime as dt
import requests

from .locale import *
from .callbacks import NavigationCallback
from .utils import *
from .keyboards.diary import *
from .FSM.diary import MarksPeriodForm

from db.models import Account

from ITschool import learner_client

admin_router = Router()

@admin_router.message(Command("captcha"))
async def try_captcha(message: Message):
    vals = message.text.split(" ")
    
    if len(vals) != 2:
        message.answer("Uncorrect input")
        return
    
    captcha_answer = vals[1]
    
    verify_data = {
        "answer": captcha_answer,
        "captchaType": "esiacaptcha"
    }
               
    learner_client
                            
    req = requests.post("https://esia.gosuslugi.ru/captcha/api/public/v2/verify", headers=learner_client.esia_login_data["headers"], cookies=learner_client.esia_login_data["cookies"], data=verify_data)

    verify_token = req.json()["verify_token"]
                            
    params = {
        "guid": learner_client.esia_login_data["guid"],
        "verify_token": verify_token
    }
                            
    req = requests.post("https://esia.gosuslugi.ru/aas/oauth2/api/anomaly/captcha/verify", params=params)

@admin_router.message(Command("captcha"))
async def try_captcha(message: Message):
    vals = message.text.split(" ")
    
    if len(vals) != 2:
        message.answer("Uncorrect input")
        return
    
    captcha_answer = vals[1]
    
    verify_data = {
        "answer": captcha_answer,
        "captchaType": "esiacaptcha"
    }
                            
    req = requests.post("https://esia.gosuslugi.ru/captcha/api/public/v2/verify", headers=learner_client.esia_login_data["headers"], cookies=learner_client.esia_login_data["cookies"], data=verify_data)

    verify_token = req.json()["verify_token"]
                            
    params = {
        "guid": learner_client.esia_login_data["guid"],
        "verify_token": verify_token
    }
                            
    req = requests.post("https://esia.gosuslugi.ru/aas/oauth2/api/anomaly/captcha/verify", params=params)
    
    message.answer(f"{req.json()}")
    learner_client.wait_captcha = False
    