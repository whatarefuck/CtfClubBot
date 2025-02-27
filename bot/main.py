import asyncio
import logging

from aiogram import Bot, Dispatcher
from handlers import (
    add_competition_router,
    add_task_router,
    start_router,
    my_tasks_router,
    missed_deadlines_router,
    heal_router,
    leaderboard_router,
    my_profile_router,
)
from settings import config

from bot.tasks import sync_education_tasks

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(token=config.BOT_TOKEN)
# Диспетчер
dp = Dispatcher()

dp.include_routers(
    start_router,
    add_task_router,
    add_competition_router,
    my_tasks_router,
    missed_deadlines_router,
    heal_router,
    leaderboard_router,
    my_profile_router,
)


# Запуск процесса поллинга новых апдейтов
async def main():
    # Запускаем задачу синхронизации задач
    asyncio.create_task(sync_education_tasks())  # Фоновая задача
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
