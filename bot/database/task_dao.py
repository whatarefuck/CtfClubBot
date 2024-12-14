from database.models import Task
from datetime import datetime

from database.user_dao import UserDAO


class TaskDao:
    """Data access object for Task"""
    def __init__(self, session):
        self.session = session

    def create_task(self, name: str, description: str, deadline: datetime, url: str,user_id:int):
        """Create task in db at /add_task"""
        new_task = Task(

            name=name,
            description=description,
            deadline=deadline,
            url=url,
            assigned_user_id = user_id

           
        )
        print(new_task.__dict__)
        self.session.add(new_task)
        self.session.commit()
        self.session.refresh(new_task)
        return new_task

    def create_tasks_for_students(self, task_name: str, task_description: str, task_deadline: datetime, task_url: str, students:str):
        """Create tasks for all students excluding specific users"""
        
        for student in students:
            
            self.create_task(
                name=task_name,
                description=task_description,
                deadline=task_deadline,
                url=task_url,
                user_id=student.id,
            )
            print(f"Task created for student: {student.id}")

