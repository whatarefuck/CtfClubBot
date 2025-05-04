from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from database.db import get_db
from database.user_dao import UserDAO
from logging import getLogger
from database.models import User

logger = getLogger(__name__)


class Notifications:
    """Класс для уведомлений"""

    def __init__(self, bot: Bot):
        self.bot = bot

    async def _say_students(self, message: str):
        """Уведомить всех студентов о чем-то.

        :param message: Значение сообщения.
        """
        with get_db() as session:
            user_dao = UserDAO(session)
            students = user_dao.get_all_students()
            for student in students:
                try:
                    await self.bot.send_message(chat_id=student.tg_id, text=message)
                    logger.info(
                        f"Sent {message} to {student.full_name} - @{student.username}"
                    )
                except TelegramBadRequest:
                    logger.warning(
                        f"Чат @{student.username} - {student.full_name} с не найден."
                    )

    async def _say_teachers(self, message: str):
        """Уведомить всех учителей о чем-то.

        :param message: Значение сообщения.
        """
        with get_db() as session:
            user_dao = UserDAO(session)
            teachers = user_dao.get_teachers()
            for teacher in teachers:
                try:
                    await self.bot.send_message(chat_id=teacher.tg_id, text=message)
                    logger.info(
                        f"Sent {message} to {teacher.full_name} - @{teacher.username}"
                    )
                except TelegramBadRequest:
                    logger.warning(
                        f"Чат @{teacher.username} - {teacher.full_name} с не найден."
                    )

    async def _say_student(self, student: User, message: str):
        """Написать студенту о чем-то."""
        try:
            await self.bot.send_message(text=message, chat_id=student.tg_id)
            logger.info(f"Sent {message} to {student.full_name} - @{student.username}")
        except TelegramBadRequest:
            logger.warning(
                f"Чат @{student.username} - {student.full_name} с не найден."
            )

    async def say_about_deadline_fail(self, message: str):
        await self._say_teachers(message)
