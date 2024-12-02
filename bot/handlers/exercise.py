from aiogram.filters.command import Command
from aiogram import types
from aiogram import Router
from sqlalchemy.exc import IntegrityError
from utils.root_me import scribe_root_me
from database.db import get_db
from database.task_dao import TaskDao
from states.user_states import addingtask
add_task_router = Router()
from aiogram.fsm.context import FSMContext
import datetime



# Хэндлер на команду /add_task
@add_task_router.message(Command("add_task"))
async def get_name(message: types.Message, state: FSMContext):
    
    await message.reply("Введите название")
    await state.set_state(addingtask.name)


@add_task_router.message(addingtask.name)
async def get_description(message: types.Message, state: FSMContext):
    name = message.text
    await state.update_data(name=name)
    await message.reply("Введите описание")
    await state.set_state(addingtask.description)

@add_task_router.message(addingtask.description)
async def get_url(message: types.Message, state: FSMContext):
    description = message.text
    await state.update_data(description=description)
    await message.reply("Введите ccылку")
    await state.set_state(addingtask.url)

@add_task_router.message(addingtask.url)
async def get_deadline(message: types.Message, state: FSMContext):
    url = message.text
    await state.update_data(url=url)
    await message.reply("Введите дедлайн")
    await state.set_state(addingtask.deadline)


@add_task_router.message(addingtask.deadline)
async def save_task(message: types.Message, state: FSMContext):
    deadline = message.text
    await state.update_data(deadline=deadline)
    task_form_data = await state.get_data()
    try:
        with get_db() as db:
            task_dao = TaskDao(db)
            name = task_form_data.get("name")
            description= task_form_data.get("description")
            url= task_form_data.get("url")
            print(name)
            
            task_dao.create_task(name, description, url,deadline)
            await message.reply('Запись задачи в БД сохранена!')
    except IntegrityError:
        await message.reply("Ошибка сохранения задачи в БД")


    


    