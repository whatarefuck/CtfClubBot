import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    tg_id = Column(Integer, index=True)
    username = Column(String, unique=True, index=True)
    full_name = Column(String)
    root_me_nickname = Column(String)
    lives = Column(Integer, default=3)
    points = Column(Integer, default=30)
    violations = Column(Integer, default=0)
    tasks = relationship("Task", back_populates="assigned_user")
    participations = relationship("Participation", back_populates="user")

    def __repr__(self):
        return f"@{self.username} - {self.full_name}>"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)

    deadline = Column(DateTime)
    assigned_user_id = Column(Integer, ForeignKey("users.id"))
    completed = Column(Boolean, default=False)
    url = Column(String)

    assigned_user = relationship("User", back_populates="tasks")

    @property
    def is_expired(self):
        """Проверка, истек ли дедлайн задачи."""
        return datetime.datetime.now() >= self.deadline


class Competition(Base):
    __tablename__ = "competitions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    date = Column(DateTime, default=datetime.datetime.utcnow)
    points = Column(Integer)
    participations = relationship("Participation", back_populates="competition")


class Participation(Base):
    __tablename__ = "participations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    competition_id = Column(Integer, ForeignKey("competitions.id"))
    points_awarded = Column(Integer, default=0)

    user = relationship("User", back_populates="participations")
    competition = relationship("Competition", back_populates="participations")


class Violation(Base):
    __tablename__ = "violations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    description = Column(String)
    date = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User")
