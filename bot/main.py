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
    mark_students_router,
)
from settings import config
from middlewares import AuthMiddleware
from tasks import sync_education_tasks
from tasks import send_event_notifications


import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

# ---------- Logging setup ----------
# Требуется, чтобы `config` был уже импортирован ранее (from settings import config)

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

# Всегда логируем в stdout
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.INFO)

handlers = [stream_handler]

# Если prod — лог в /var/log/ctfbotrun.log (с ротацией). При проблемах — fallback в /tmp
if getattr(config, "ENV", "").lower() == "prod":
    primary_log = Path("/var/log/ctfbotrun.log")
    fallback_log = Path("/tmp/ctfbotrun.log")
    fallback_used = None
    file_handler = None

    # Попытка создать /var/log/ctfbotrun.log
    try:
        # Создаём папку, если вдруг отсутствует (обычно не требуется)
        primary_log.parent.mkdir(parents=True, exist_ok=True)
        # Попытка создать файл (если ещё нет) — может выбросить PermissionError
        primary_log.touch(mode=0o644, exist_ok=True)

        # Ротация: 10 MB на файл, 5 бэкапов
        file_handler = RotatingFileHandler(
            filename=str(primary_log),
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        handlers.append(file_handler)

    except Exception as err_primary:
        # Если не удалось записать в /var/log — попробуем fallback (/tmp)
        print(f"Warning: cannot create/write {primary_log!s}: {err_primary}. Trying fallback {fallback_log!s}.", file=sys.stderr)
        try:
            fallback_log.parent.mkdir(parents=True, exist_ok=True)
            fallback_log.touch(mode=0o644, exist_ok=True)
            file_handler = RotatingFileHandler(
                filename=str(fallback_log),
                maxBytes=5 * 1024 * 1024,
                backupCount=3,
                encoding="utf-8",
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(logging.INFO)
            handlers.append(file_handler)
            fallback_used = fallback_log
        except Exception as err_fallback:
            # Не получилось ни туда — печатаем в stderr и продолжаем только с stdout
            print(f"Error: cannot create/write fallback log {fallback_log!s}: {err_fallback}. Continuing with stdout only.", file=sys.stderr)
            file_handler = None

# Сбрасываем существующие хэндлеры (чтобы не дублировать при повторных импортax) и добавляем новые
if root_logger.handlers:
    root_logger.handlers.clear()

for h in handlers:
    root_logger.addHandler(h)

# После установки хэндлеров — пишем запусковые сообщения
root_logger.info("Logger initialized. stdout logging enabled.")
if getattr(config, "ENV", "").lower() == "prod":
    # Определим, куда именно пишем (ищем последний файловый хэндлер)
    file_handlers = [h for h in handlers if isinstance(h, (RotatingFileHandler, logging.FileHandler))]
    if file_handlers:
        # Берём путь из первого файлового handler'а
        log_path = getattr(file_handlers[0], "baseFilename", None)
        root_logger.info("Also logging to file: %s", log_path)
    else:
        root_logger.warning("ENV=prod but no file logger could be created; logs will go to stdout only.")

# Ограничим шум от некоторых библиотек (опционально)
logging.getLogger("aiogram").setLevel(logging.INFO)
logging.getLogger("apscheduler").setLevel(logging.INFO)
# ---------- End logging setup ----------

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
    types.BotCommand(command="/mark_students", description="Отметить присутствующих"),
]

dp.include_routers(
    start_router,
    mark_students_router,
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
