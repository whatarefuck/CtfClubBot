from datetime import datetime

from aiogram import Router, types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from database.competition_dao import CompetitionDao
from database.db import get_db
from sqlalchemy.exc import IntegrityError
from states.competition_states import CompetitionForm

add_competition_router = Router()


# Хэндлер на команду /add_competition
@add_competition_router.message(Command("add_competition"))
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer("Название мероприятия.")
    await state.set_state(CompetitionForm.name)


@add_competition_router.message(CompetitionForm.name)
async def get_name(message: types.Message, state: FSMContext):
    name = message.text
    await state.update_data(name=name)
    await message.reply("Введите описание")
    await state.set_state(CompetitionForm.description)


@add_competition_router.message(CompetitionForm.description)
async def get_description(message: types.Message, state: FSMContext):
    description = message.text
    await state.update_data(description=description)
    await message.reply("Введите количество баллов")
    await state.set_state(CompetitionForm.points)


@add_competition_router.message(CompetitionForm.points)
async def get_points(message: types.Message, state: FSMContext):
    points = int(message.text)  # хз что не так как испровить

    await state.update_data(points=points)
    await message.reply("Введите дедлайн(формат " "д.м.г" ")")
    await state.set_state(CompetitionForm.date)


@add_competition_router.message(CompetitionForm.date)
async def get_deadline(message: types.Message, state: FSMContext):
    date = message.text
    date = datetime.strptime(date, "%d.%m.%Y")
    await state.update_data(date=date)
    competition_form_data = await state.get_data()
    try:
        with get_db() as db:
            competition_dao = CompetitionDao(db)
            name = competition_form_data.get("name")
            description = competition_form_data.get("description")
            date = competition_form_data.get("date")
            points = competition_form_data.get("point")
            print(name)

            competition_dao.add_competition(
                name=name,
                description=description,
                date=date,
                points=points,
                participations=[],
            )
            await message.reply("Запись задачи в БД сохранена!")
            await state.clear()  # Сбрасываем состояние
    except IntegrityError:
        await message.reply("Ошибка сохранения задачи в БД")
        await state.clear()  # Сбрасываем состояние
