from database.models import Participation


class ParticipationDAO:
    def __init__(self, session):
        self.session = session

    def mark_participation(self, competition_id: int, student_ids: list[int]):
        """Синхронный метод для отметки участия"""
        try:
            for student_id in student_ids:
                existing = (
                    self.session.query(Participation)
                    .filter_by(user_id=student_id, competition_id=competition_id)
                    .first()
                )

                if not existing:
                    new_participation = Participation(
                        user_id=student_id, competition_id=competition_id
                    )
                    self.session.add(new_participation)

            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise e
