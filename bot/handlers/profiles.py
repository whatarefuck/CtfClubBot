from aiogram import Router
from aiogram.filters.command import Command
from aiogram.types import Message


from database.models import User

my_profile_router = Router()


@my_profile_router.message(Command("my_profile"))
async def my_profile_handler(message: Message, user: User):
    await message.reply(
        f"👤 *Профиль пользователя*\n\n"
        f"🧑 Полное имя: {user.full_name or 'Не указано'}\n"
        f"🎓 RootMe ник: {user.root_me_nickname or 'Не указано'}\n"
        f"❤️ Жизни: {user.lives}\n"
        f"⭐ Очки: {user.points}\n"
    )
