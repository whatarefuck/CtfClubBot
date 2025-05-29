from aiogram import Router
from aiogram.filters.command import Command
from aiogram.types import Message
from database.db import get_db
from database.user_dao import UserDAO
from database.models import User
from logging import getLogger
from typing import Optional

logger = getLogger(__name__)

leaderboard_router = Router()


def format_top_rating(top_rating: list[User]) -> list[str]:
    """Формирует строки для топ-20 пользователей."""
    messages = ["🏆 Лидеры (Топ-20):"]
    if not top_rating:
        messages.append("Пока что никто не заработал баллов в топ-20.")
    else:
        for idx, top_user in enumerate(top_rating, start=1):
            messages.append(f"{idx}. @{top_user.username} — {top_user.points} баллов")
    return messages


def format_user_status(user: User, top_rating: list[User]) -> list[str]:
    """Формирует статус текущего пользователя."""
    messages = []
    in_top = any(top_user.id == user.id for top_user in top_rating)
    
    messages.append(f"\n📊 Ваш статус: @{user.username} — {user.points} баллов")
    
    if in_top and user.points > 0:
        rank = next((i + 1 for i, u in enumerate(top_rating) if u.id == user.id), 0)
        messages.append(f"🎉 Вы на {rank}-м месте в топ-20!")
    else:
        if user.points == 0:
            messages.append("😔 У вас пока нет баллов. Решайте задачи, чтобы попасть в топ!")
        else:
            last_top_score = top_rating[-1].points if top_rating else 0
            needed = last_top_score - user.points + 1
            messages.append(
                f"👉 Чтобы войти в топ-20, нужно ещё {needed} балл(ов)."
            )
    return messages


@leaderboard_router.message(Command("leaderboard"))
async def leaderboard_handler(message: Message, user: User) -> None:
    """
    Показывает топ-20 пользователей по очкам, всех пользователей (включая с 0 баллов),
    а также статус текущего пользователя.
    """
    with get_db() as db:
        user_dao = UserDAO(db)

        # Логируем баллы текущего пользователя
        logger.info(f"Пользователь @{user.username} имеет {user.points} баллов")

        # Получаем топ-20 пользователей (только с ненулевыми баллами)
        top_rating = [u for u in user_dao.leaderboard(limit=20) if u.points > 0]

        # Формируем сообщение
        leaderboard_message = format_top_rating(top_rating)
        user_status = format_user_status(user, top_rating)
        leaderboard_message.extend(user_status)

        await message.answer("\n".join(leaderboard_message))