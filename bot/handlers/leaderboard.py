from aiogram import Router
from aiogram.filters.command import Command
from aiogram.types import Message

from database.db import get_db


from database.user_dao import UserDAO

leaderboard_router = Router()


@leaderboard_router.message(Command("leaderboard"))
async def leaderboard_handler(message: Message):

    with get_db() as db:
        user_dao = UserDAO(db)

        await message.reply(str(user_dao.leaderboard()))
