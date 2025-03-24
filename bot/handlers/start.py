from aiogram import Router, types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from database.db import get_db
from database.user_dao import UserDAO
from sqlalchemy.exc import IntegrityError
from states.user_states import UserRegisteryForm
from utils.root_me import scribe_root_me

from database.models import User
from logging import getLogger

logger = getLogger()
start_router = Router()


@start_router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext, user: User):
    logger.info(f"Запуск /start {user}")
    if user:
        await message.answer("Привет, ты можешь посмотреть свой профиль командой /my_profile.")
        return
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
    tg_id = message.from_user.id
    root_me_nickname = scribe_root_me(root_me_link)
    user_form_data = await state.get_data()
    try:
        with get_db() as db:
            user_dao = UserDAO(db)
            fullname = user_form_data.get("full_name")
            print(fullname)
            username = message.from_user.username
            user_dao.create_user(username, fullname, root_me_nickname, tg_id)
            await message.answer("Хорошо, можете попробовать вызвать команды из меню. Например, /my_tasks")
            await state.clear()  # Сбрасываем состояние после успешной регистрации
    except IntegrityError as e:
        logger.error(e)
        await message.reply("Ошибка сохранения пользователя в БД")
        await state.clear()  # Сбрасываем состояние в случае ошибки
