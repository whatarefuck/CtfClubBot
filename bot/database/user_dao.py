from database.models import User



from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound

def get_user_id_by_username(db_session: Session, username: str):
    try:
        user = db_session.query(User).filter(User.username == username).one()
        return user.id
    except NoResultFound:
        return None
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
        print(new_user.__dict__)
        self.session.add(new_user)
        self.session.commit()
        self.session.refresh(new_user)
        return new_user

    def get_all_students(self):
        """Get all students excluding specific users"""
        excluded_user_id = [get_user_id_by_username('vb_vik'), get_user_id_by_username('iambainazar')]

        
        return self.session.query(User).filter(User.id.notin_(excluded_user_id)).all()