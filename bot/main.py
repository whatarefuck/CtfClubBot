import asyncio
import logging
import sentry_sdk

from tasks import restore_student_lives
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone

from aiogram import Bot, Dispatcher, types

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
from tasks import send_event_notifications

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(token=config.BOT_TOKEN)
# Диспетчер
dp = Dispatcher()

commands = [
    types.BotCommand(command="/start", description="Запустить бота"),
    types.BotCommand(command="/my_tasks", description="Мои невыполненные задачи"),
    types.BotCommand(command="/my_profile", description="Мой профиль"),
    types.BotCommand(command="/leaderboard", description="Рейтинг участников"),
    types.BotCommand(command="/heal", description="Исцелиться"),
    types.BotCommand(command="/add_task", description="Отправить студентам задачу"),
    types.BotCommand(
        command="/missed_deadlines", description="Посмотреть пропущенные дедлайны"
    ),
    types.BotCommand(command="/add_competition", description="Создать мероприятие"),
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

sentry_sdk.init(
    dsn=config.SENTRY_DSN,
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
    environment=config.ENV,
)

dp.message.middleware(AuthMiddleware())


async def main():
    scheduler = AsyncIOScheduler()
    # Добавляем периодическую задачу восстановления жизней
    # Выполняется каждое 10-е число месяца в 00:00 по МСК (UTC+3)
    scheduler.add_job(
        restore_student_lives,
        trigger=CronTrigger(
            day=10,  # Каждый день
            hour=0,  # Полночь
            minute=0,
            timezone=timezone("Europe/Moscow"),
        ),
        id="restore_lives",
        name="Восстановление жизней студентов",
        replace_existing=True,
    )
    scheduler.add_job(
        send_event_notifications,
        args=[bot],
        trigger=CronTrigger(
            hour=6,
            minute=0,
            timezone=timezone("Europe/Moscow"),
        ),
        id="send_event_notifications",
        name="Отправка уведомлений о событиях",
        replace_existing=True,
    )
    # Запускаем планировщик
    scheduler.start()
    await bot.set_my_commands(commands)
    # Запускаем задачу синхронизации задач
    asyncio.create_task(sync_education_tasks(bot))  # Фоновая задача
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
