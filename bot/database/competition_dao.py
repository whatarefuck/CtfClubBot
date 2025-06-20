from datetime import datetime

from database.models import Competition


class CompetitionDao:
    """Data access object for Competition"""

    def __init__(self, session):
        self.session = session

    def add_competition(
        self,
        name: str,
        description: str,
        date: datetime,
        points: int,
        participations: int,
    ):
        """Add competition in db at /add_competition"""
        new_competition = Competition(
            name=name,
            description=description,
            date=date,
            points=points,
            participations=participations,
        )
        self.session.add(new_competition)
        self.session.commit()
        self.session.refresh(new_competition)
        return new_competition

    def get_all_competition(self):
        return self.session.query(Competition).all()

    def get_events_between(self, start_time: datetime, end_time: datetime):
        """Получить события в заданном временном диапазоне."""
        return (
            self.session.query(Competition)
            .filter(Competition.date >= start_time, Competition.date < end_time)
            .all()
        )
