from aiogram import Router
from aiogram.filters.command import Command
from aiogram.types import Message
from aiogram.enums import ParseMode

from database.db import get_db


from database.user_dao import UserDAO

my_profile_router = Router()


@my_profile_router.message(Command("my_profile"))
async def my_profile_handler(message: Message):

    with get_db() as db:
        user_dao = UserDAO(db)
        message.from_user.username

        await message.reply(
            str(user_dao.myprofile(message.from_user.username)),
            parse_mode=ParseMode.HTML,
        )
