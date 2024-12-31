from aiogram.fsm.state import State, StatesGroup


class CompetitionForm(StatesGroup):
    name = State()
    description = State()
    date = State()
    points = State()
    participations = State()
