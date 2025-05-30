from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime
from database.models import Participation
from database.models import User
from database.models import Competition


class ParticipationDAO:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def mark_participation(self, competition_id: int, student_ids: list[int]):
        """
        Отмечает участие студентов в мероприятии
        :param competition_id: ID мероприятия
        :param student_ids: Список ID студентов
        """
        try:
            # Проверяем существование мероприятия
            competition = await self.session.get(Competition, competition_id)
            if not competition:
                raise ValueError(f"Мероприятие с ID {competition_id} не найдено")

            # Для каждого студента создаем или обновляем запись об участии
            for student_id in student_ids:
                # Проверяем существование студента
                student = await self.session.get(User, student_id)
                if not student:
                    continue  # или можно вызвать исключение

                # Ищем существующую запись об участии
                existing_participation = await self.session.execute(
                    select(Participation).where(
                        and_(
                            Participation.user_id == student_id,
                            Participation.competition_id == competition_id,
                        )
                    )
                )
                existing_participation = existing_participation.scalar_one_or_none()

                if existing_participation:
                    # Если запись уже существует, можно обновить (например, дату)
                    existing_participation.participation_date = datetime.utcnow()
                else:
                    # Создаем новую запись об участии
                    new_participation = Participation(
                        user_id=student_id,
                        competition_id=competition_id,
                        points_awarded=competition.points,  # если начисляются баллы
                    )
                    self.session.add(new_participation)

            await self.session.commit()
            return True
        except Exception as e:
            await self.session.rollback()
            raise e

    async def get_participants(self, competition_id: int):
        """
        Получает список участников мероприятия
        :param competition_id: ID мероприятия
        :return: Список объектов Participation
        """
        result = await self.session.execute(
            select(Participation).where(Participation.competition_id == competition_id)
        )
        return result.scalars().all()
