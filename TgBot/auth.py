from aiogram import Router, F
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from string import ascii_letters

from TgBot.locale import *
from .keyboards import *
from .callbacks import AuthCallback
from .FSM import AuthForm

from db.models import Account, Person
from db import session

auth_router = Router(name='auth')

@auth_router.message(Command('start'))
async def start(message: Message):
    user = await Account(message.from_user.id).get_account()
    if user:
        await message.answer(welcome_text(user.first_name), reply_markup=MainMenuKeyboard())
    else:
        await message.answer(start_text, reply_markup=AuthKeyboard())

@auth_router.callback_query(AuthCallback.filter(F.action == "start"))
async def auth_start(query: CallbackQuery):
    user = await Account(query.from_user.id).get_account()
    if user:
        await query.message.edit_text(already_login_text, parse_mode="Markdownv2")
        return
    await query.message.edit_text(allow_personal_data_text, reply_markup=PersonalDataKeyboard())
            
@auth_router.callback_query(AuthCallback.filter(F.action == "cancel"))
async def auth_cancel(query: CallbackQuery):
    await query.message.edit_text(cancel_text, reply_markup=AuthKeyboard())
    await query.answer()

@auth_router.callback_query(AuthCallback.filter(F.action == "allow"))
async def auth_allow(query: CallbackQuery, state: FSMContext):
    user = await Account(query.from_user.id).get_account()
    if user:
        await query.message.answer(already_login_text, parse_mode="Markdownv2")
        await query.message.delete()
        return 

    await state.set_state(AuthForm.name)
    await query.message.answer(name_text)
    await query.answer()

@auth_router.callback_query(AuthCallback.filter(F.action == "deny"))
async def auth_deny(query: CallbackQuery, state: FSMContext):
    await state.clear()
    await query.message.answer(olny_one_person_error_text, parse_mode='Markdownv2', reply_markup=AuthKeyboard())
    await query.message.delete()

@auth_router.message(AuthForm.name)
async def procces_name(message: Message, state: FSMContext):
    await state.update_data(first_name=message.text.capitalize())
    await state.set_state(AuthForm.last_name)
    await message.answer(last_name_text)

@auth_router.message(AuthForm.last_name)
async def procces_last_name(message: Message, state: FSMContext):
    await state.update_data(last_name=message.text.capitalize())
    await message.answer(verification_text, reply_markup=VerificationKeyboard())

@auth_router.callback_query(AuthCallback.filter())
async def procces_verification(query: CallbackQuery, callback_data: AuthCallback, state: FSMContext):
    text = None
    match callback_data.action:
        case "passport":
            text = verification_passport_text
        case "snils":
            text = verification_snils_text
        case "born":
            text = verification_born_text

    await query.message.edit_text(text)
    await state.update_data({"verf_type": callback_data.action})
    await state.set_state(AuthForm.verification)

@auth_router.message(AuthForm.verification)
async def procces_last_name(message: Message, state: FSMContext):
    await state.update_data(verf=message.text.capitalize())
    data = await state.get_data()
    first_name = data["first_name"]
    last_name = data["last_name"]
    verf = data["verf"]
    match data["verf_type"]:
        case "passport":
            person_id = await Person.get_id_by_passport(first_name, last_name, verf)
            account_id = await Person.is_authenticated_by_passport(first_name, last_name, verf)
        case "snils":
            person_id = await Person.get_id_by_snils(first_name, last_name, verf)
            account_id = await Person.is_authenticated_by_snils(first_name, last_name, verf)
        case "born":
            person_id = await Person.get_id_by_born(first_name, last_name, verf)
            account_id = await Person.is_authenticated_by_born(first_name, last_name, verf)
    
    
    if person_id:
        if account_id:
            if account_id == message.from_user.id:
                await message.answer(already_login_text, parse_mode="Markdownv2", reply_markup=ToMainMenuKeyboard())
            else:
                await message.answer(already_login_text, parse_mode="Markdownv2", reply_markup=AuthKeyboard())
            return
        await Account(message.from_user.id, first_name=first_name).create()
        await Person.set_account_id(person_id, message.from_user.id)
        await message.answer(success_login_text, parse_mode="Markdownv2", reply_markup=ToMainMenuKeyboard())
    else:
        await message.answer(person_error_text, parse_mode="Markdownv2", reply_markup=AuthKeyboard())
