import asyncio
from logging import getLogger

from database.db import get_db
from database.user_dao import UserDAO

from utils.root_me import get_solved_tasks_of_student

from database.notification_dao import NotificationsDAO

from datetime import datetime

logger = getLogger()


async def sync_education_tasks():
    Notifications = NotificationsDAO()
    while True:
        with get_db() as session:
            # Fetch all users with their tasks
            dao = UserDAO(session)
            users = dao.get_all_students_with_tasks()

            for user in users:

                if user.root_me_nickname:
                    try:
                        solved_tasks = await get_solved_tasks_of_student(
                            user.root_me_nickname
                        )

                        for task in user.tasks:
                            current_time = datetime.now()
                            if task.completed == None:
                                if task.deadline <= current_time:
                                    task.completed = False
                                    logger.info(
                                        f"Task {task.id} for user {user.id} marked as failed (deadline passed)"
                                    )
                                    user.lives -= 1
                                    # Если задача была завершена, но теперь не решена, уменьшаем HP
                                    logger.info(
                                        f"Decreased HP for user: {user.username}. Current HP: {user.lives}"
                                    )

                                else:
                                    task.completed = task.name in solved_tasks

                                if user.lives <= 0:
                                    # Если HP достигло 0, уведомляем админов
                                    await Notifications._say_admins(
                                        f"User {user.username} has reached 0 HP!"
                                    )
                                    logger.info(
                                        f"Notified admins about {user.username} reaching 0 HP."
                                    )

                        session.commit()
                        logger.info(f"Synced tasks for user: {user.username}")
                    except Exception as e:
                        logger.error(f"Error syncing tasks for {user.username}: {e}")
                await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(sync_education_tasks())
