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

    def get_by_id(self, user_id: int) -> User | None:
        """
        Возвращает пользователя по его внутреннему ID (PK) или None,
        чтобы можно было получить актуальные данные из БД.
        """
        return (
            self.session
            .query(User)
            .filter(User.id == user_id)
            .one_or_none()
        )

    def create_user(
        self, username: str, full_name: str, root_me_nickname: str, tg_id: int
    ) -> User:
        """Создаёт нового пользователя при /start."""
        new_user = User(
            tg_id=tg_id,
            username=username,
            full_name=full_name,
            root_me_nickname=root_me_nickname,
            # points и lives подхватят default из модели
        )
        self.session.add(new_user)
        self.session.commit()
        self.session.refresh(new_user)
        return new_user

    def get_all_students(self) -> list[User]:
        """Получить всех студентов (исключая учителей по tg_id)."""
        return (
            self.session.query(User)
            .filter(User.tg_id.notin_(config.teacher_ids))
            .all()
        )

    def get_all_active_students(self) -> list[User]:
        """Получить всех студентов с живыми (lives > 0) и имеющих username."""
        return (
            self.session.query(User)
            .filter(User.username.isnot(None), User.lives > 0)
            .all()
        )

    def get_user_id_by_username(self, username: str) -> int | None:
        """Вернуть внутренний ID пользователя по username или None."""
        user = (
            self.session.query(User)
            .filter(User.username == username)
            .first()
        )
        return user.id if user else None

    def get_user_by_tg_id(self, tg_id: int) -> User | None:
        """Получить пользователя по его Telegram ID."""
        return (
            self.session.query(User)
            .filter(User.tg_id == tg_id)
            .first()
        )

    def get_all_students_with_tasks(self) -> list[User]:
        """Получить всех студентов вместе с их невыполненными заданиями."""
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

    def heal(self, user: User) -> None:
        """Обменять 10 опыта на 3 жизни."""
        user.lives += 3
        user.points -= 10
        self.session.commit()
        self.session.refresh(user)

    def get_teachers(self) -> list[User]:
        """Получить всех учителей (старшекурсников) по tg_id."""
        teachers = (
            self.session.query(User)
            .filter(User.tg_id.in_(config.teacher_ids))
            .all()
        )
        logger.info(f"Получены учителя: {teachers}")
        return teachers

    def leaderboard(self, limit: int = 20) -> list[User]:
        """Извлечь топ-`limit` пользователей, сортируя по убыванию points."""
        return (
            self.session.query(User)
            .order_by(User.points.desc())
            .limit(limit)
            .all()
        )
