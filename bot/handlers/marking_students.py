from aiogram import F, Router
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.user_dao import UserDAO
from database.competition_dao import CompetitionDao
from database.db import get_db

mark_students_router = Router()

# Инициализация DAO
with get_db() as db:
    UserDao = UserDAO(db)
    CompetitionDAO = CompetitionDao(db)
    EVENTS = CompetitionDAO.get_all_competition()  # список объектов Competition
    STUDENTS = UserDao.get_all_students()          # список объектов Student

# Кэш для хранения выбранных студентов
user_selections = {}

@mark_students_router.message(Command("mark_students"))
async def show_events(message: Message):
    builder = InlineKeyboardBuilder()
    for event in EVENTS:
        builder.button(
            text=f"{event.name} ({event.date.strftime('%d.%m.%Y')})", 
            callback_data=f"event_{event.id}"
        )
    builder.adjust(1)
    await message.answer(
        "Выберите мероприятие:",
        reply_markup=builder.as_markup()
    )

@mark_students_router.callback_query(F.data.startswith("event_"))
async def select_students(callback: CallbackQuery):
    event_id = int(callback.data.split("_")[1])
    # Находим мероприятие по ID
    competition = next((e for e in EVENTS if e.id == event_id), None)
    
    if not competition:
        await callback.answer("Мероприятие не найдено!")
        return
    
    user_selections[callback.from_user.id] = {
        "event_id": event_id,
        "selected": set(),
        "competition_name": competition.name
    }
    
    # Отправляем первую страницу студентов
    await show_students_page(callback, page=0)

async def show_students_page(callback: CallbackQuery, page: int):
    user_data = user_selections.get(callback.from_user.id)
    if not user_data:
        await callback.answer("Сессия устарела, начните заново!")
        return
    
    # Разбиваем студентов на страницы по 5 человек
    students_per_page = 5
    start_idx = page * students_per_page
    page_students = STUDENTS[start_idx:start_idx + students_per_page]
    total_pages = (len(STUDENTS) + students_per_page - 1) // students_per_page
    
    builder = InlineKeyboardBuilder()
    for student in page_students:
        status = "✅" if student.id in user_data["selected"] else "◻️"
        builder.button(
            text=f"{status} {student.full_name} ({student.username})",
            callback_data=f"toggle_{student.id}_{page}"
        )
    
    # Кнопки навигации
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="◀️ Назад", callback_data=f"page_{page-1}"))
    if (page + 1) * students_per_page < len(STUDENTS):
        nav_buttons.append(InlineKeyboardButton(text="▶️ Вперед", callback_data=f"page_{page+1}"))
    nav_buttons.append(InlineKeyboardButton(text="⏭️ Подтвердить", callback_data="confirm"))
    
    builder.row(*nav_buttons)
    
    await callback.message.edit_text(
        f"Выберите студентов для мероприятия {user_data['competition_name']} [Страница {page+1} из {total_pages}]",
        reply_markup=builder.as_markup()
    )

@mark_students_router.callback_query(F.data.startswith("toggle_"))
async def toggle_student(callback: CallbackQuery):
    _, student_id, page = callback.data.split("_")
    student_id = int(student_id)
    page = int(page)
    
    selected = user_selections[callback.from_user.id]["selected"]
    if student_id in selected:
        selected.remove(student_id)
    else:
        selected.add(student_id)
    
    await show_students_page(callback, page)

@mark_students_router.callback_query(F.data.startswith("page_"))
async def change_page(callback: CallbackQuery):
    page = int(callback.data.split("_")[1])
    await show_students_page(callback, page)

@mark_students_router.callback_query(F.data == "confirm")
async def confirm_selection(callback: CallbackQuery):
    user_data = user_selections[callback.from_user.id]
    selected_ids = user_data["selected"]
    
    selected_students = [
        f"{s.full_name} ({s.username})" 
        for s in STUDENTS 
        if s.id in selected_ids
    ]
    
    if not selected_students:
        await callback.answer("Не выбрано ни одного студента!")
        return
    
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Подтвердить посещения", callback_data="final_confirm")
    builder.button(text="❌ Отменить", callback_data="cancel")
    
    await callback.message.edit_text(
        f"Вы выбрали {len(selected_students)} студентов для мероприятия \"{user_data['competition_name']}\":\n\n"
        + "\n".join(selected_students),
        reply_markup=builder.as_markup()
    )

@mark_students_router.callback_query(F.data == "final_confirm")
async def final_confirmation(callback: CallbackQuery):
    user_data = user_selections[callback.from_user.id]
    
    # Здесь должна быть логика сохранения в БД
    # Например:
    # with get_db() as db:
    #     ParticipationDAO(db).mark_participation(
    #         user_data['event_id'],
    #         list(user_data['selected'])
    #     )
    
    await callback.message.edit_text(
        f"Готово! {len(user_data['selected'])} студентов отмечены на мероприятии \"{user_data['competition_name']}\"."
    )
    del user_selections[callback.from_user.id]

@mark_students_router.callback_query(F.data == "cancel")
async def cancel_action(callback: CallbackQuery):
    if callback.from_user.id in user_selections:
        del user_selections[callback.from_user.id]
    await callback.message.edit_text("Действие отменено.")