from aiogram.fsm.state import State, StatesGroup


class MarkStudentsState(StatesGroup):
    selecting_event = State()
    selecting_students = State()
    confirmation = State()