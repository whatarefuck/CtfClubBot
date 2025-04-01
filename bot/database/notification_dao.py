from database.models import User
from settings import config
from sqlalchemy.orm import joinedload
from logging import getLogger
from aiogram.types import Message 

ADMIN_NICKNAMES = config.ADMIN_NICKNAMES.split()
bot=config.BOT_TOKEN

class  NotificationsDAO:
    """Data access object for User"""
    
    async def _say_admins(self, message: Message):
        for admin_nick in ADMIN_NICKNAMES:
            try:
                await bot.send_message(chat_id=8121070643, text=message)
                
            except Exception as e:
                pass
    
    async def _say_teachers(sel, message: str):
        pass

    async def say_task_failed(self, message: str):
        pass