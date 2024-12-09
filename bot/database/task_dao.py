from database.models import Task
import datetime

from database.user_dao import UserDAO


class TaskDao:
    """Data access object for Task"""
    def __init__(self, session):
        self.session = session

    def create_task(self, name: str, description: str, deadline: datetime, url: str):
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

    def create_tasks_for_students(self, user_dao: UserDAO, task_name: str, task_description: str, task_deadline: datetime, task_url: str):
        """Create tasks for all students excluding specific users"""
        students = user_dao.get_all_students(self)
        for student in students:
            self.create_task(
                name=task_name,
                description=task_description,
                deadline=task_deadline,
                url=task_url,
                assigned_user_id=student.id,
            )
            print(f"Task created for student: {student.id}")

