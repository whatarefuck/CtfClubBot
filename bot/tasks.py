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
                            student_message = (
                                f"Ты потерял 1 HP за задачу {task.name}. 😢 Пожалуйста, старайся выполнять задания вовремя, чтобы избежать потерь.\
                                      Если у тебя есть вопросы или трудности, не стесняйся обращаться за помощью в общий чат."
                            )
                            logger.info(student_message)
                            await notify._say_student(student_message)

                    session.commit()
                    logger.info(f"Synced tasks for user: {user.username}")
                    # except Exception as e:
                    #     logger.error(f"Error syncing tasks for {user.username}: {e.}")
                await asyncio.sleep(60)
        await asyncio.sleep(0.1)


if __name__ == "__main__":
    asyncio.run(sync_education_tasks())
