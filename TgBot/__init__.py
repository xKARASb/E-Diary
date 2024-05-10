from os import getenv
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher

from .auth import auth_router
from .diary import diary_router
from .timetable import timetable_router

load_dotenv()

bot_token = getenv("BOT-TOKEN")

bot = Bot(token=bot_token)
dp = Dispatcher()

dp.include_router(auth_router)
dp.include_router(diary_router)
dp.include_router(timetable_router)

async def start_bot():
    await dp.start_polling(bot, handle_signals=True)

async def stop_bot():
    await dp.stop_polling()
            