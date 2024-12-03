from aiogram.fsm.state import StatesGroup, State


class UserRegisteryForm(StatesGroup):
    full_name = State()

    root_me_nickname = State()




class TaskForm(StatesGroup):
    name=State()
    url=State()
    description=State()
    deadline=State()
