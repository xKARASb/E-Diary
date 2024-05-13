from os import getenv
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.filters.exception import ExceptionTypeFilter
from ITschool.exceptions import ServerUnaccessible

from .auth import auth_router
from .diary import diary_router
from .timetable import timetable_router
from .keyboards import ToMainMenuKeyboard

load_dotenv()

bot_token = getenv("BOT-TOKEN")

bot = Bot(token=bot_token)
dp = Dispatcher()

dp.include_router(auth_router)
dp.include_router(diary_router)
dp.include_router(timetable_router)

@dp.error(ExceptionTypeFilter(ServerUnaccessible))
async def handle_serverunaccesible_exception(event):
    await event.update.callback_query.message.edit_text("Сервер электронного дневника временно не доступен 🥲\nРазработчик уже разбирается в проблеме!", reply_markup=ToMainMenuKeyboard())
    await bot.send_message(1810265462, "Сервер электронного дневника не доступен!!!")

async def start_bot():
    await dp.start_polling(bot, handle_signals=True)

async def stop_bot():
    await dp.stop_polling()
            