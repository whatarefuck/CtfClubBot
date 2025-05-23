import asyncio
from aiogram import Bot
from logging import getLogger

from utils.notifications import Notifications
from database.db import get_db
from database.user_dao import UserDAO

from utils.root_me import get_solved_tasks_of_student


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
                        if not task.completed and task.is_expired:
                            user.lives -= 1
                            user.violations += 1
                            teacher_message = (
                                f"Задача {task.name} истек у студента {user}."
                            )
                            logger.info(teacher_message)
                            notify = Notifications(bot)
                            await notify.say_about_deadline_fail(teacher_message)

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


if __name__ == "__main__":
    asyncio.run(sync_education_tasks())
