from database.models import Competition
from datetime import datetime




class CompetitionDao:
    """Data access object for Task"""
    def __init__(self, session):
        self.session = session

    def add_competition(self, name: str, description: str, date: datetime, points: int,participations:int):
        """Add competition in db at /add_competition"""
        new_competition = Competition(

            name=name,
            description=description,
            date=date,
            points=points,
            participations = participations

           
        )
        self.session.add(new_competition)
        self.session.commit()
        self.session.refresh(new_competition)
        return new_competition