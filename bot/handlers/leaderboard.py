from aiogram import Router
from aiogram.filters.command import Command
from aiogram.types import Message

from database.db import get_db


from database.user_dao import UserDAO
from database.models import User
leaderboard_router = Router()


@leaderboard_router.message(Command("leaderboard"))
async def leaderboard_handler(message: Message, user: User):
    with get_db() as db:
        user_dao = UserDAO(db)
        rating = user_dao.leaderboard()
        if not rating:
            await message.answer("Пока что никто не заработал баллов, рейтинга нет.")
            return

        leaderboard_message = "🏆 Лидеры:\n"
        for idx, top_user in enumerate(rating, start=1):
            leaderboard_message += f"{idx}. @{top_user.username} - {top_user.points}\n"

        # Check if current user is in the top ratings by username
        current_username = message.from_user.username
        user_in_top = any(top_user.username == current_username for top_user in rating)

        if user_in_top:
            leaderboard_message += "Поздравляем! Вы в топ-20!"
        else:
            # If rating is not empty, calculate points needed
            points_needed = max(top_user.points for top_user in rating) - user.points + 1
            leaderboard_message += f"Тебя нет в топе. Не расстраивайся, тебе осталось заработать всего {points_needed}"

    await message.answer(leaderboard_message)
