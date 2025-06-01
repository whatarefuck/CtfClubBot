from database.db import get_db
from database.models import User
from logging import getLogger


logger = getLogger(__name__)


def reset_all_user_points():
    with get_db() as db:
        # Сбрасываем points до 0 для всех пользователей
        updated = db.query(User).update({"points": 0})
        db.commit()
        logger.info(f"Обновлено {updated} пользователей, все баллы сброшены до 0.")

        # Проверяем результат
        users = db.query(User).all()
        for user in users:
            logger.info(f"User @{user.username}: {user.points} points")


if __name__ == "__main__":
    reset_all_user_points()
