from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from string import ascii_letters

from TgBot.locale import *
from .keyboards import *
from .callbacks import AuthCallback
from .FSM import AuthForm

from db.models import Learner, Account
from db import session

auth_router = Router(name='auth')

@auth_router.message(Command('start'))
async def start(message: Message):
    user = await Account.get_account(message.from_user.id)
    if user:
        await message.answer(welcome_text(user.learner.first_name), reply_markup=MainMenuKeyboard())
    else:
        await message.answer(start_text, reply_markup=AuthKeyboard())

@auth_router.callback_query(AuthCallback.filter(F.action == "start"))
async def auth_start(query: CallbackQuery):
    user = await Account.get_account(query.from_user.id)
    if user:
        await query.message.edit_text(already_login_text, parse_mode="Markdownv2")
        return
    
    await query.message.edit_text(allow_personal_data_text, reply_markup=PersonalDataKeyboard())
            
@auth_router.callback_query(AuthCallback.filter(F.action == "cancel"))
async def auth_cancel(query: CallbackQuery):
    await query.message.edit_text(cancel_text, reply_markup=AuthKeyboard())
    await query.answer()

@auth_router.callback_query(AuthCallback.filter(F.action == "allow"))
async def auth_cancel(query: CallbackQuery, state: FSMContext):
    user = await Account.get_account(query.from_user.id)
    if user:
        await query.message.answer(already_login_text, parse_mode="Markdownv2")
        await query.message.delete()
        return 

    await state.set_state(AuthForm.name)
    await query.message.answer(name_text)
    await query.answer()

@auth_router.callback_query(AuthCallback.filter(F.action == "confirm"))
async def auth_confirm(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    db_session = await session()
    learner = (await Learner.get_learner_by_name(db_session, data["name"], data["last_name"])).one()
    account = Account(query.from_user.id)
    learner.account_id = query.from_user.id
    db_session.add(account)

    await db_session.commit()
    await db_session.close()

    await query.message.answer("Ты успешно авторизовался\!", parse_mode='Markdownv2', reply_markup=None)
    await query.message.delete()
    await state.clear()

@auth_router.callback_query(AuthCallback.filter(F.action == "deny"))
async def auth_deny(query: CallbackQuery, state: FSMContext):
    await state.clear()
    await query.message.answer(olny_one_person_error_text, parse_mode='Markdownv2', reply_markup=AuthKeyboard())
    await query.message.delete()

@auth_router.message(AuthForm.name)
async def procces_name(message: Message, state: FSMContext):
    #TODO Check name to valid, check exsising name
    await state.update_data(name=message.text.capitalize())
    await state.set_state(AuthForm.last_name)
    await message.answer(last_name_text)

@auth_router.message(AuthForm.last_name)
async def procces_last_name(message: Message, state: FSMContext):
    await state.update_data(last_name=message.text.capitalize())

    data = await state.get_data()
    db_session = await session()
    learners = (await Learner.get_learner_by_name(db_session, data["name"], data["last_name"])).all()
    await db_session.close()
    if len(learners) == 1:
        if learners[0].account_id:
            await state.clear()
            await message.answer(already_registered_text, parse_mode="Markdownv2")
            return
        await message.answer(
            person_confirm_user_text(
                learners[0].first_name,
                learners[0].last_name,
                learners[0].birthday.strftime("%d-%m-%Y"),
                learners[0].group.course,
                learners[0].group.liter
                ),
            reply_markup=ConfirmUserKeyboard()
            )
    elif len(learners) == 0:
        await message.answer(person_error_text, parse_mode='Markdownv2', reply_markup=AuthKeyboard())
        await state.clear()

@auth_router.message(AuthForm.course)
async def procces_course(message: Message, state: FSMContext):
    if message.text.isdigit() and int(message.text) > 0 and int(message.text) < 12:
        await state.update_data(course=message.text)
        await state.set_state(AuthForm.letter)
        await message.answer(letter_text)
    else:
        await message.answer(course_error_text)

@auth_router.message(AuthForm.letter)
async def procces_course(message: Message, state: FSMContext):
    if message.text.lower() in ascii_letters:
        await state.update_data(course=message.text)
        await state.set_state(AuthForm.letter)
        # await message.answer(letter_text)
    else:
        await message.answer(letter_error_text)


