from database.models import User
from settings import config

ADMIN_NICKNAMES = config.ADMIN_NICKNAMES.split()


class UserDAO:
    """Data access object for User"""

    def __init__(self, session):
        self.session = session

    def create_user(self, username: str, full_name: str, root_me_nickname: str):
        """Create user in db at /start"""
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

        return self.session.query(User).filter(User.username.notin_(ADMIN_NICKNAMES)).all()
    def get_user_id_by_username(self, username: str):
        user = self.session.query(User).filter(User.username == username).first()
        if user:
            return user.id
        return None

