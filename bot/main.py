import asyncio
import logging

from aiogram import Bot, Dispatcher, types, Router
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
from middlewares import AuthMiddleware
from tasks import sync_education_tasks

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(token=config.BOT_TOKEN)
# Диспетчер
dp = Dispatcher()

commands = [
    types.BotCommand(command='/start', description='Запустить бота'),
    types.BotCommand(command='/my_tasks', description='Мои невыполненные задачи'),
    types.BotCommand(command='/my_profile', description='Мой профиль'),
    types.BotCommand(command='/leaderboard', description='Рейтинг участников'),
    types.BotCommand(command='/heal', description='Исцелиться'),
    types.BotCommand(command='/add_task', description='Отправить студентам задачу'),
    types.BotCommand(command='/missed_deadlines', description='Посмотреть пропущенные дедлайны'),
    types.BotCommand(command='/add_competition', description='Создать мероприятие'),
]

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

dp.message.middleware(AuthMiddleware())

# Запуск процесса поллинга новых апдейтов
async def main():
    # Запускаем задачу синхронизации задач
    asyncio.create_task(sync_education_tasks())  # Фоновая задача
    await bot.set_my_commands(commands)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
