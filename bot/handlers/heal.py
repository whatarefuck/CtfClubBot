from aiogram import Router
from aiogram.filters.command import Command
from aiogram.types import Message
from settings import config
from database.db import get_db


from database.user_dao import UserDAO

from database.models import User

heal_router = Router()


@heal_router.message(Command("heal"))
async def heal_handler(message: Message, user: User):
    if user.lives > config.HEAL_LIMIT:
        await message.answer("У тебя достаточно HP, так держать!")
    elif user.points < config.minimum_xp_count_to_heal:
        await message.answer(
            f"Извини, у тебя всего {user.points} баллов, нужно минимум {config.minimum_xp_count_to_heal}."
        )
    with get_db() as db:
        user_dao = UserDAO(db)
        updated_user = user_dao.heal(user)
        await message.answer(
            f"Увеличил твою HP на одну 🩹\n Теперь у тебя {updated_user.lives}❤️."
        )
