from aiogram.types import Message
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Callable, Dict, Any, Awaitable, Optional

from database.db import get_db
from database.user_dao import UserDAO
from logging import getLogger

logger = getLogger()

REGISTER_HANDLERS = ["cmd_start", "get_fullname", "save_user"]

def get_original_callback_name(handler: Callable) -> Optional[str]:
    """
    Attempt to extract the name of the original callback (e.g., 'cmd_start')
    from an aiogram 3.x middleware 'handler'.

    Returns:
        The callback function's __name__ if found, otherwise None.
    """
    # 'handler' is usually a wrapped function in aiogram 3.x
    raw_handler = getattr(handler, "__wrapped__", None)
    if raw_handler is not None:
        # raw_handler.__self__ is typically the HandlerObject
        handler_object = getattr(raw_handler, "__self__", None)
        if handler_object is not None and hasattr(handler_object, "callback"):
            # callback is the actual function you defined with @router.message(...)
            callback_func = handler_object.callback
            return callback_func.__name__

    return None

class AuthMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        tg_id = event.from_user.id
        handler_name = get_original_callback_name(handler)
        logger.info(f"{handler_name=}")
        with get_db() as session:
            dao = UserDAO(session)
            user = dao.get_user_by_tg_id(tg_id)
            if not user and handler_name not in REGISTER_HANDLERS:
                await event.answer("Не нашел вас в списке пользователей, зарегистрируйтесь командой /start")
                return

            data["user"] = user

        return await handler(event, data)
