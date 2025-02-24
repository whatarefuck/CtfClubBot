from aiogram import Router
from aiogram.filters.command import Command
from aiogram.types import Message

from database.db import get_db


from database.user_dao import UserDAO

heal_router = Router()


@heal_router.message(Command("heal"))
async def heal_handler(message: Message):

    with get_db() as db:
        user_dao = UserDAO(db)
        message.from_user.username

        await message.reply(str(user_dao.heal(message.from_user.username)))
