import asyncio
from datetime import datetime, timedelta
from aiogram import Bot
from logging import getLogger
from pytz import timezone

from utils.notifications import Notifications
from database.db import get_db
from database.user_dao import UserDAO

from database.competition_dao import CompetitionDao
from utils.root_me import get_solved_tasks_of_student

import os


logger = getLogger()


async def sync_education_tasks(bot: Bot):
    while True:
        with get_db() as session:
            # Fetch all users with their tasks
            dao = UserDAO(session)
            users = dao.get_all_students_with_tasks()
            for user in users:
                if user.root_me_nickname:
                    # try:
                    solved_tasks = await get_solved_tasks_of_student(
                        user.root_me_nickname
                    )
                    for task in user.tasks:
                        task.completed = task.name in solved_tasks
                        if (
                            not task.completed and task.is_expired
                            and not task.violation_recorded
                        ):
                            user.lives -= 1
                            user.violations += 1
                            task.violation_recorded = True  # Отмечаем, что нарушение обработано
                            teacher_message = (
                                f"Задача {task.name} истека у студента {user}."
                            )
                            logger.info(teacher_message)
                            notify = Notifications(bot)
                            await notify.say_about_deadline_fail(
                                teacher_message
                            )
                            student_message = (
                                f"Ты потерял 1 HP за задачу {task.name}. 😢 "
                                "Пожалуйста, старайся выполнять задания вовремя, "
                                "чтобы избежать потерь. Если у тебя есть вопросы "
                                "или трудности, не стесняйся обращаться за помощью "
                                "в общий чат."
                            )
                            logger.info(student_message)
                            await notify._say_student(user, student_message)

                    session.commit()
                    logger.info(f"Synced tasks for user: {user.username}")
                    # except Exception as e:
                    #     logger.error(f"Error syncing tasks for {user.username}: {e.}")
                await asyncio.sleep(60)
        await asyncio.sleep(0.1)


async def restore_student_lives():
    """Восстановление жизней всех активных студентов до 3-х."""
    try:
        with get_db() as session:
            dao = UserDAO(session)
            # Получаем всех "живых" пользователей (HP > 0)
            active_users = dao.get_all_active_students()

            count = 0

            for user in active_users:
                if user.lives < 3:  # Восстанавливаем только если меньше максимума
                    user.lives = 3
                    logger.info(f"Здоровье {user.username} = 3")

                    count += 1

            if count > 0:
                session.commit()
                logger.info(f"Восстановлены жизни для {count} студентов.")
            else:
                logger.info("Нет студентов, нуждающихся в восстановлении жизней.")
    except Exception as e:
        logger.error(f"Ошибка при восстановлении жизней: {e}")


async def send_event_notifications(bot: Bot):
    """Отправка уведомлений о событиях за 1 день и в день мероприятия."""
    try:
        moscow_tz = timezone('Europe/Moscow')
        now = datetime.now(moscow_tz)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        tomorrow_start = today_start + timedelta(days=1)
        tomorrow_end = today_start + timedelta(days=2)

        with get_db() as session:
            dao = CompetitionDao(session)
            today_events = dao.get_events_between(today_start, today_end)
            tomorrow_events = dao.get_events_between(
                tomorrow_start, tomorrow_end
            )

            for event in today_events:
                logger.info(f"Уведомление о событии сегодня: {event.name}")
                notify = Notifications(bot)
                for participation in event.participations:
                    user = participation.user
                    msg = (
                        f"Сегодня: {event.name} в "
                        f"{event.date.strftime('%H:%M')}."
                    )
                    await notify._say_student(user, msg)

            for event in tomorrow_events:
                logger.info(f"Уведомление о событии завтра: {event.name}")
                notify = Notifications(bot)
                for participation in event.participations:
                    user = participation.user
                    msg = (
                        f"Завтра: {event.name} в "
                        f"{event.date.strftime('%H:%M')}."
                    )
                    await notify._say_student(user, msg)

    except Exception as e:
        logger.error(f"Ошибка при отправке уведомлений: {e}")


#if __name__ == "__main__":
#    asyncio.run(sync_education_tasks())
# Закомментировал __main__-блок, потому что этот файл подключается как модуль в основном боте,
# и запуск его напрямую приведёт к ошибке из-за отсутствия аргумента bot.