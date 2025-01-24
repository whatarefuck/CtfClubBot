import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from bot.database.models import User, Task
from bot.utils.root_me import get_solved_tasks_of_student
from database.db import get_db
from database.user_dao import UserDAO
from logging import getLogger

logger = getLogger()

async def sync_education_tasks():
    while True:
        with get_db() as session:
            # Fetch all users with their tasks
            dao = UserDAO(session)
            users = dao.get_all_students_with_tasks()
            for user in users:
                if user.root_me_nickname:
                    # try:
                    solved_tasks = await get_solved_tasks_of_student(user.root_me_nickname)
                    for task in user.tasks:
                        task.completed = task.name in solved_tasks
                    session.commit()
                    logger.info(f"Synced tasks for user: {user.username}")
                    # except Exception as e:
                    #     logger.error(f"Error syncing tasks for {user.username}: {e.}")
                await asyncio.sleep(60)


if __name__=="__main__":
    asyncio.run(sync_education_tasks())
