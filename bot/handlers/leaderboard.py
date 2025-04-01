from aiogram import Router, types
from aiogram.filters.command import Command
from aiogram.types import Message

from database.db import get_db


from database.user_dao import UserDAO

leaderboard_router = Router()


@leaderboard_router.message(Command("leaderboard"))
async def leaderboard_handler(message: types.Message):

    with get_db() as db:
        user_dao = UserDAO(db)

        
        students=user_dao.leaderboard()
        ranking_table = []
        for student in students:
            ranking_table.append({"ФИО": student.full_name, "Очки": student.points})

        top_20 = ranking_table[:20]

# Формируем сообщение для отправки
        message = "Топ 20 студентов:\n"
        for i, student in enumerate(top_20, start=1):
            message += f"{i}. {student['ФИО']} - {student['Очки']} очков\n"

# Отправляем сообщение
        await message.reply(message)



