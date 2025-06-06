from aiogram import Router
from aiogram.filters.command import Command
from aiogram.types import Message

from database.db import get_db


from database.task_dao import TaskDao

from database.models import User

# Создаем роутер для обработки команд
my_tasks_router = Router()

# Хендлер для команды /my_tasks


@my_tasks_router.message(Command("my_tasks"))
async def my_tasks_handler(message: Message, user: User):
    with get_db() as db:
        task_dao = TaskDao(db)
        tasks = task_dao.user_tasks(user)
        task_info = ""
        if tasks:
            for missed_task in tasks:
                task_info += f"Задача: {missed_task.name}\nОписание: {missed_task.description}\nСсылка: {missed_task.url}\n\n"
        else:
            task_info = "Пока нет никаких задач."

        await message.reply(task_info)
