from database.db import get_db
from database.models import User

def reset_user_points():
    with get_db() as db:
        # Сбрасываем points до 0 для всех пользователей с points = 30
        updated = db.query(User).filter(User.points == 30).update({"points": 0})
        db.commit()
        print(f"Обновлено {updated} пользователей с 30 баллами до 0.")

        # Для проверки: выводим всех пользователей и их баллы
        users = db.query(User).all()
        for user in users:
            print(f"User @{user.username}: {user.points} points")

if __name__ == "__main__":
    reset_user_points()
