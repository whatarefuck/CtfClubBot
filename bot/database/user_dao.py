from database.models import User
from settings import config
from sqlalchemy.orm import joinedload
from logging import getLogger

logger = getLogger(__name__)
ADMIN_NICKNAMES = config.ADMIN_NICKNAMES.split()


class UserDAO:
    """Data access object for User"""

    def __init__(self, session):
        self.session = session

    def create_user(
        self, username: str, full_name: str, root_me_nickname: str, tg_id: int
    ):
        """Create user in self.session at /start"""
        new_user = User(
            tg_id=tg_id,
            username=username,
            full_name=full_name,
            root_me_nickname=root_me_nickname,
        )
        self.session.add(new_user)
        self.session.commit()
        self.session.refresh(new_user)
        return new_user

    def get_all_students(self) -> list[User]:
        """Get all students excluding specific users"""

        return (
            self.session.query(User).filter(User.tg_id.notin_(config.teacher_ids)).all()
        )

    def get_all_active_students(self):
        return (
            self.session.query(User)
            .filter(User.username.notin_(ADMIN_NICKNAMES), User.lives > 0)
            .all()
        )

    def get_user_by_tg_id(self, tg_id: int) -> User:
        """Получить пользователя по его телеграм ID.

        :param tg_id: Телеграмм айди
        """
        return self.session.query(User).filter(User.tg_id == tg_id).first()

    def get_all_students_with_tasks(self):
        """Получить всех пользователей вместе с их заданиями"""

        users = (
            self.session.query(User)
            .filter(User.tg_id.notin_(config.teacher_ids))
            .options(joinedload(User.tasks))
            .all()
        )
        # Оставляем только невыполненные задачи
        for user in users:
            user.tasks = [task for task in user.tasks if not task.completed]
        return users

    def heal(self, user: User):
        """Обменять 10 опыта на 1 HP."""

        user.lives += 3
        user.points -= 10

        self.session.commit()
        self.session.refresh(user)

    def get_teachers(self):
        """Получить всех старшекурсников."""
        teachers = (
            self.session.query(User).filter(User.tg_id.in_(config.teacher_ids)).all()
        )
        logger.info(f"Получены учителя - {teachers}")
        return teachers

    def leaderboard(self):
        """Извлекаем всех студентов, сортируя по убыванию баллов."""
        return self.session.query(User).order_by(User.points.desc()).limit(20).all()
