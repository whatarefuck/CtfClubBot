from aiogram.fsm.state import State, StatesGroup


class UserRegisteryForm(StatesGroup):
    full_name = State()

    root_me_nickname = State()


class TaskForm(StatesGroup):
    name = State()
    url = State()
    description = State()
    deadline = State()
