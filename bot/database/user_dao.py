from database.models import User
from settings import config
from sqlalchemy.orm import joinedload

ADMIN_NICKNAMES = config.ADMIN_NICKNAMES.split()


class UserDAO:
    """Data access object for User"""

    def __init__(self, session):
        self.session = session

    def create_user(self, username: str, full_name: str, root_me_nickname: str):
        """Create user in self.session at /start"""
        new_user = User(
            username=username,
            full_name=full_name,
            root_me_nickname=root_me_nickname,
        )
        self.session.add(new_user)
        self.session.commit()
        self.session.refresh(new_user)
        return new_user

    def get_all_students(self):
        """Get all students excluding specific users"""

        return (
            self.session.query(User).filter(User.username.notin_(ADMIN_NICKNAMES)).all()
        )

    def get_user_id_by_username(self, username: str):
        user = self.session.query(User).filter(User.username == username).first()
        if user:
            return user.id
        return None

    def get_all_students_with_tasks(self):
        """Получить всех пользователей вместе с их заданиями"""

        users = (
            self.session.query(User)
            .filter(User.username.notin_(ADMIN_NICKNAMES))
            .options(joinedload(User.tasks))
            .all()
        )
        # Оставляем только невыполненные задачи
        for user in users:
            user.tasks = [task for task in user.tasks if not task.completed]
        return users

    def heal(self, username: str):
        user = self.session.query(User).filter(User.username == username).first()
        if user.points >= 10:
            # Находим пользователя по Telegram никнейму

            if not user:
                return {"error": "User not found"}

            # Добавляем жизни и отнимаем очки

            user.lives += 3
            user.points -= 10

            # Сохраняем изменения в базе данных
            self.session.commit()
            self.session.refresh(user)

            return {
                "success": f"User {user.username} now has {user.lives} lives and {user.points} points."
            }

        else:
            self.session.rollback()
            return "Недостаточно поинтов"

    def leaderboard(self):
        # Извлекаем всех студентов, сортируя по убыванию баллов
        students = self.session.query(User).order_by(User.points.desc()).all()

        # Формируем таблицу с ФИО и количеством баллов
        ranking_table = []
        for student in students:
            ranking_table.append({"ФИО": student.full_name, "Очки": student.points})

        return ranking_table

    def myprofile(self, username=str):
        user = self.session.query(User).filter(User.username == username).first()

        if user:
            return {
                "success": (
                    f"User: {user.username}\n"
                    f"Root-Me: {user.root_me_nickname}\n"
                    f"Points: {user.points}\n"
                    f"HP: {user.lives}\n"
                    f"Violations: {user.violations}\n"
                    f"Participations: {user.participations}"
                )
            }
        else:
            return None
