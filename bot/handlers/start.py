from aiogram import Router, types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from database.db import get_db
from database.user_dao import UserDAO
from sqlalchemy.exc import IntegrityError
from states.user_states import UserRegisteryForm
from utils.root_me import scribe_root_me

start_router = Router()


@start_router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer("Привет! Отправь мне свое ФИО.")
    await state.set_state(UserRegisteryForm.full_name)


@start_router.message(UserRegisteryForm.full_name)
async def get_fullname(message: types.Message, state: FSMContext):
    fullname = message.text
    await state.update_data(full_name=fullname)
    await message.reply("Скиньте ссылку вашего профиля в https://www.root-me.org/")
    await state.set_state(UserRegisteryForm.root_me_nickname)


@start_router.message(UserRegisteryForm.root_me_nickname)
async def save_user(message: types.Message, state: FSMContext):
    root_me_link = message.text
    root_me_nickname = scribe_root_me(root_me_link)
    user_form_data = await state.get_data()
    try:
        with get_db() as db:
            user_dao = UserDAO(db)
            fullname = user_form_data.get("full_name")
            print(fullname)
            username = message.from_user.username
            user_dao.create_user(username, fullname, root_me_nickname)
            await message.reply("Пользователь сохранен в БД")
            await state.clear()  # Сбрасываем состояние после успешной регистрации
    except IntegrityError:
        await message.reply("Ошибка сохранения пользователя в БД")
        await state.clear()  # Сбрасываем состояние в случае ошибки
