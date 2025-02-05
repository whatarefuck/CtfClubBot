
from aiogram import Router
from aiogram.filters.command import Command
from aiogram.types import Message

from database.db import get_db


from database.task_dao import TaskDao
from database.user_dao import UserDAO

# Создаем роутер для обработки команд
my_tasks_router = Router()

# Хендлер для команды /my_tasks


@my_tasks_router.message(Command('my_tasks'))
async def my_tasks_handler(message: Message):
    with get_db() as db:
        task_dao = TaskDao(db)
        user_dao = UserDAO(db)
        tasks = task_dao.user_tasks(user_dao.get_user_id_by_username(message.from_user.username))
        if tasks:
            task_info = ""
            for task in tasks:
                task_info += f"Задача: {task.name}\nОписание: {task.description}\nСсылка: {task.url}\n\n"

        await message.reply(task_info)
