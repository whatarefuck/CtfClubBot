from aiogram.filters.command import Command
from aiogram import types
from aiogram import Router
from sqlalchemy.exc import IntegrityError
from utils.root_me import scribe_root_me
from database.db import get_db
from database.task_dao import TaskDao
from database.user_dao import UserDAO
from states.user_states import TaskForm

from aiogram.fsm.context import FSMContext
from datetime import datetime

add_task_router = Router()

# Хэндлер на команду /add_task
@add_task_router.message(Command("add_task"))
async def cmd_add_task(message: types.Message, state: FSMContext):
    
    await message.reply("Введите название")
    await state.set_state(TaskForm.name)


@add_task_router.message(TaskForm.name)
async def get_name(message: types.Message, state: FSMContext):
    name = message.text
    await state.update_data(name=name)
    await message.reply("Введите описание")
    await state.set_state(TaskForm.description)

@add_task_router.message(TaskForm.description)
async def get_description(message: types.Message, state: FSMContext):
    description = message.text
    await state.update_data(description=description)
    await message.reply("Введите ccылку")
    await state.set_state(TaskForm.url)

@add_task_router.message(TaskForm.url)
async def get_url(message: types.Message, state: FSMContext):
    url = message.text
    await state.update_data(url=url)
    await message.reply("Введите дедлайн(формат "'д.м.г'")")
    await state.set_state(TaskForm.deadline)


@add_task_router.message(TaskForm.deadline)
async def get_deadline(message: types.Message, state: FSMContext):
    deadline = message.text
    deadline=datetime.strptime(deadline, "%d.%m.%Y")
    await state.update_data(deadline=deadline)
    task_form_data = await state.get_data()
    try:
        with get_db() as db:
            task_dao = TaskDao(db)
            name = task_form_data.get("name")
            description= task_form_data.get("description")
            url= task_form_data.get("url")
            print(name)
            
            task_dao.create_task(name, description, deadline,url)
            task_dao.create_tasks_for_students(
                 user_dao=UserDAO,
                 task_name=name,
                 task_description=description,
                 task_deadline=deadline,
                 task_url=url
)
            await message.reply('Запись задачи в БД сохранена!')
    except IntegrityError:
        await message.reply("Ошибка сохранения задачи в БД")


    


    