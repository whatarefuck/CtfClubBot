from database.models import Task
import datetime
class TaskDao:
    """Data access object for Task"""
    def __init__(self, session):
        self.session = session

    def create_task(self, name: str, description: str, deadline: datetime,url:str):
        """Create task in db at /add_task"""
        new_task = Task(
            name=name,
            description=description,
            deadline=deadline,
            url=url,
        )
        print(new_task.__dict__)
        self.session.add(new_task)
        self.session.commit()
        self.session.refresh(new_task)
        return new_task