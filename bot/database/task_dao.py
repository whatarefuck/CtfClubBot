from datetime import datetime

from database.models import Task

from database.models import User


class TaskDao:
    """Data access object for Task"""

    def __init__(self, session):
        self.session = session

    def create_task(
        self, name: str, description: str, deadline: datetime, url: str, user_id: int
    ):
        """Create task in db at /add_task"""
        new_task = Task(
            name=name,
            description=description,
            deadline=deadline,
            url=url,
            assigned_user_id=user_id,
        )

        self.session.add(new_task)
        self.session.commit()
        self.session.refresh(new_task)
        return new_task

    def create_tasks_for_students(
        self,
        task_name: str,
        task_description: str,
        task_deadline: datetime,
        task_url: str,
        students: str,
    ):
        """Create tasks for all students excluding specific users"""

        for student in students:
            self.create_task(
                name=task_name,
                description=task_description,
                deadline=task_deadline,
                url=task_url,
                user_id=student.id,
            )
            print(f"Task created for student : {student.id}")

    def user_tasks(self, user: User):

        current_time = datetime.now()  # Получаем текущее время в UTC
        return (
            self.session.query(Task)
            .filter(
                Task.assigned_user_id == user.id,
                Task.completed == False,
                Task.deadline > current_time,
            )
            .all()
        )

    def missed_user_tasks(self, user: User):

        current_time = datetime.now()  # Получаем текущее время в UTC
        return (
            self.session.query(Task)
            .filter(
                Task.assigned_user_id == user.id,
                Task.completed == False,
                Task.deadline < current_time,
            )
            .all()
        )

    def score_for_tasks(self, S_min: int, N: int, N_total: int, time: float):

        R_time = min(time, 0.35)
        score = max(S_min, 500 * (1 - N / N_total) * (1 + R_time))
        return (score)

    def decided_users(self, task_name: str):
        completed_tasks = self.session.query(Task).filter(
            Task.name == task_name,
            Task.completed == True
        ).all()
        user_ids = {task.assigned_user_id for task in completed_tasks}
        

        return len(user_ids)

    def all_users(self, task_name: str):
        tasks = self.session.query(Task).filter(
            Task.name == task_name,

        ).all()
        user_ids = {task.assigned_user_id for task in tasks}
        
        return len(user_ids)

    def index_of_time(self, task_name: str, assigned_user_id: int):
        task = self.session.query(Task).filter(
            Task.name == task_name,
            Task.assigned_user_id == assigned_user_id,
            Task.completed == True
        ).first()

        if task is None or task.deadline is None:
            return 0  # Задача не найдена или у задачи нет дедлайна

        time_taken = datetime.now() - task.deadline
        time_until_deadline = task.deadline - datetime.now()  # отрицательное, если просрочено

        # Абсолютные значения времени в секундах
        time_taken_sec = abs(time_taken.total_seconds())
        time_until_deadline_sec = abs(time_until_deadline.total_seconds())

        if time_taken_sec == 0:
            return None  # избегаем деления на ноль

        ratio = round(time_until_deadline_sec / time_taken_sec, 2)
        
        return ratio
