from aiogram import Router
from aiogram.filters.command import Command
from aiogram.types import Message

from database.db import get_db


from database.task_dao import TaskDao
from database.user_dao import UserDAO

missed_deadlines_router = Router()


@missed_deadlines_router.message(Command('missed_deadlines'))
async def missed_deadlines_handler(message: Message):
    with get_db() as db:
        task_dao = TaskDao(db)
        user_dao = UserDAO(db)
        missed_tasks = task_dao.missed_user_tasks(user_dao.get_user_id_by_username(message.from_user.username))
        missed_task_info = ""
        if missed_tasks:
            for missed_task in missed_tasks:
                missed_task_info += f"Задача: {missed_task.name}\nОписание: {missed_task.description}\nСсылка: {missed_task.url}\n\n"
        else:
            missed_task_info = "У вас нет просроченных задач."
        await message.reply(missed_task_info)
