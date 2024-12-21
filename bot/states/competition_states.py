from aiogram.fsm.state import StatesGroup, State






class CompetitionForm(StatesGroup):
    name=State()
    description=State()
    date=State()
    points=State()
    participations=State()
