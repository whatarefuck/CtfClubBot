from aiogram import F, Router
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.user_dao import UserDAO
from database.competition_dao import CompetitionDao
from database.Participationdao import ParticipationDAO
from database.db import get_db
from states.mark_students_states import MarkStudentsState

mark_students_router = Router()

# Инициализация DAO
with get_db() as db:
    UserDao = UserDAO(db)
    CompetitionDAO = CompetitionDao(db)

@mark_students_router.message(Command("mark_students"))
async def show_events(message: Message, state: FSMContext):
    builder = InlineKeyboardBuilder()
    EVENTS = CompetitionDAO.get_all_competition()  # список объектов Competition
    for event in EVENTS:
        builder.button(
            text=f"{event.name} ({event.date.strftime('%d.%m.%Y')})",
            callback_data=f"event_{event.id}",
        )
    builder.adjust(1)
    
    await state.set_state(MarkStudentsState.selecting_event)
    await message.answer("Выберите мероприятие:", reply_markup=builder.as_markup())

@mark_students_router.callback_query(F.data.startswith("event_"), StateFilter(MarkStudentsState.selecting_event))
async def select_students(callback: CallbackQuery, state: FSMContext):
    event_id = int(callback.data.split("_")[1])
    EVENTS = CompetitionDAO.get_all_competition()  # список объектов Competition
    competition = next((e for e in EVENTS if e.id == event_id), None)

    if not competition:
        await callback.answer("Мероприятие не найдено!")
        return

    await state.update_data(
        event_id=event_id,
        selected=set(),
        competition_name=competition.name,
        current_page=0
    )
    await state.set_state(MarkStudentsState.selecting_students)
    
    # Отправляем первую страницу студентов
    await show_students_page(callback, state)

async def show_students_page(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected = data.get("selected", set())
    current_page = data.get("current_page", 0)
    
    # Разбиваем студентов на страницы по 5 человек
    students_per_page = 5
    start_idx = current_page * students_per_page
    STUDENTS = UserDao.get_all_students()  # список объектов Student
    page_students = STUDENTS[start_idx : start_idx + students_per_page]
    total_pages = (len(STUDENTS) + students_per_page - 1) // students_per_page

    builder = InlineKeyboardBuilder()
    for student in page_students:
        status = "✅" if student.id in selected else "◻️"
        builder.button(
            text=f"{status} {student.full_name} ({student.username})",
            callback_data=f"toggle_{student.id}",
        )

    # Кнопки навигации
    nav_buttons = []
    if current_page > 0:
        nav_buttons.append(
            InlineKeyboardButton(text="◀️ Назад", callback_data="page_prev")
        )
    if (current_page + 1) * students_per_page < len(STUDENTS):
        nav_buttons.append(
            InlineKeyboardButton(text="▶️ Вперед", callback_data="page_next")
        )
    nav_buttons.append(
        InlineKeyboardButton(text="⏭️ Подтвердить", callback_data="confirm")
    )

    builder.row(*nav_buttons)

    await callback.message.edit_text(
        f"Выберите студентов для мероприятия {data['competition_name']} [Страница {current_page+1} из {total_pages}]",
        reply_markup=builder.as_markup(),
    )

@mark_students_router.callback_query(F.data.startswith("toggle_"), StateFilter(MarkStudentsState.selecting_students))
async def toggle_student(callback: CallbackQuery, state: FSMContext):
    student_id = int(callback.data.split("_")[1])
    data = await state.get_data()
    selected = set(data.get("selected", set()))
    
    if student_id in selected:
        selected.remove(student_id)
    else:
        selected.add(student_id)
    
    await state.update_data(selected=selected)
    await show_students_page(callback, state)

@mark_students_router.callback_query(F.data.in_(["page_prev", "page_next"]), StateFilter(MarkStudentsState.selecting_students))
async def change_page(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_page = data.get("current_page", 0)
    
    if callback.data == "page_prev":
        current_page -= 1
    else:
        current_page += 1
    
    await state.update_data(current_page=current_page)
    await show_students_page(callback, state)

@mark_students_router.callback_query(F.data == "confirm", StateFilter(MarkStudentsState.selecting_students))
async def confirm_selection(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected_ids = data.get("selected", set())
    STUDENTS = UserDao.get_all_students()  # список объектов Student

    selected_students = [
        f"{s.full_name} ({s.username})" for s in STUDENTS if s.id in selected_ids
    ]

    if not selected_students:
        await callback.answer("Не выбрано ни одного студента!")
        return

    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Подтвердить посещения", callback_data="final_confirm")
    builder.button(text="❌ Отменить", callback_data="cancel")

    await state.set_state(MarkStudentsState.confirmation)
    await callback.message.edit_text(
        f"Вы выбрали {len(selected_students)} студентов для мероприятия \"{data['competition_name']}\":\n\n"
        + "\n".join(selected_students),
        reply_markup=builder.as_markup(),
    )

@mark_students_router.callback_query(F.data == "final_confirm", StateFilter(MarkStudentsState.confirmation))
async def final_confirmation(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    try:
        with get_db() as db:
            participation_dao = ParticipationDAO(db)
            participation_dao.mark_participation(
                data["event_id"], list(data["selected"])
            )

        await callback.message.edit_text(
            f"Готово! {len(data['selected'])} студентов отмечены на мероприятии \"{data['competition_name']}\"."
        )
        await state.clear()
    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}")

@mark_students_router.callback_query(F.data == "cancel", StateFilter(MarkStudentsState.confirmation))
async def cancel_action(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Действие отменено.")