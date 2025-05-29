from aiogram import Router
from aiogram.filters.command import Command
from aiogram.types import Message
from database.db import get_db
from database.user_dao import UserDAO
from database.models import User
from logging import getLogger

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


def format_all_users(all_users: list[User]) -> list[str]:
    """Формирует строки для всех пользователей."""
    messages = ["\n📋 Все пользователи:"]
    if not all_users:
        messages.append("Нет пользователей.")
    else:
        for user in all_users:
            messages.append(f"@{user.username} — {user.points} баллов")
    return messages


def format_user_status(current_user: User, top_rating: list[User]) -> list[str]:
    """Формирует статус текущего пользователя."""
    messages = []
    in_top = any(top_user.id == current_user.id for top_user in top_rating)
    if in_top and current_user.points > 0:
        messages.append(f"\n🎉 Поздравляем! Вы в топ-{len(top_rating)}!")
    else:
        if current_user.points == 0:
            messages.append("\n😔 Вы ещё не заработали баллов. Решайте задачи, чтобы попасть в топ!")
        else:
            top_score = top_rating[0].points if top_rating else 0
            needed = top_score - current_user.points + 1
            messages.append(
                f"\n😔 Вас нет в топе. Чтобы попасть на первое место, вам осталось заработать {needed} балл(ов)."
            )
    return messages


@leaderboard_router.message(Command("leaderboard"))
async def leaderboard_handler(message: Message, user: User):
    """
    Показывает топ-20 пользователей по очкам, всех пользователей (включая с 0 баллов),
    а также статус текущего пользователя.
    """
    with get_db() as db:
        user_dao = UserDAO(db)

        # Получаем свежие данные по текущему пользователю из БД
        current_user = user_dao.get_by_id(user.id)
        if current_user is None:
            await message.answer("Не могу найти ваши данные в базе.")
            return

        # Отладка: логируем баллы текущего пользователя
        logger.info(f"Пользователь @{current_user.username} имеет {current_user.points} баллов")

        # Получаем топ-20 пользователей (только с ненулевыми баллами)
        top_rating = [u for u in user_dao.leaderboard(limit=20) if u.points > 0]

        # Получаем всех пользователей
        all_users = user_dao.get_all_students()

        # Формируем сообщение
        leaderboard_message = []
        leaderboard_message.extend(format_top_rating(top_rating))
        leaderboard_message.extend(format_all_users(all_users))
        leaderboard_message.extend(format_user_status(current_user, top_rating))

        await message.answer("\n".join(leaderboard_message))
