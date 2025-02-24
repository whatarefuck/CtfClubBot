import pytest
from aiogram.fsm.context import FSMContext
from sqlalchemy.exc import IntegrityError

from bot.handlers.start import cmd_start, get_fullname, save_user


@pytest.mark.asyncio
async def test_cmd_start(mock_message, mock_fsm: FSMContext):
    mock_message.text = "/start"
    await cmd_start(mock_message, mock_fsm)

    # Verify bot response
    mock_message.answer.assert_called_once_with("Привет! Отправь мне свое ФИО.")

    # Verify state transition
    assert await mock_fsm.get_state() == "UserRegisteryForm:full_name"


@pytest.mark.asyncio
async def test_get_fullname(mock_message, mock_fsm: FSMContext):
    mock_message.text = "John Doe"
    await get_fullname(mock_message, mock_fsm)

    # Verify data storage in FSM
    data = await mock_fsm.get_data()
    assert data["full_name"] == "John Doe"

    # Verify bot response
    mock_message.reply.assert_called_once_with(
        "Скиньте ссылку вашего профиля в https://www.root-me.org/"
    )

    # Verify state transition
    assert await mock_fsm.get_state() == "UserRegisteryForm:root_me_nickname"


@pytest.mark.asyncio
async def test_save_user(
    mock_message, mock_fsm: FSMContext, mocked_db, mocked_scribe_root_me
):
    mock_message.text = "https://www.root-me.org/user"
    mock_message.from_user.username = "test_user"

    await mock_fsm.set_data({"full_name": "John Doe"})
    user_dao_mock = mocked_db.return_value.__enter__.return_value
    user_dao_mock.create_user.return_value = None

    await save_user(mock_message, mock_fsm)

    # Verify user creation in DB
    user_dao_mock.create_user.assert_called_once_with(
        "test_user", "John Doe", "mocked_nickname"
    )

    # Verify bot response
    mock_message.reply.assert_called_once_with("Запись пользователя в БД сохранена!")


@pytest.mark.asyncio
async def test_save_user_integrity_error(
    mock_message, mock_fsm: FSMContext, mocked_db, mocked_scribe_root_me
):
    mock_message.text = "https://www.root-me.org/user"
    mock_message.from_user.username = "test_user"

    await mock_fsm.set_data({"full_name": "John Doe"})
    user_dao_mock = mocked_db.return_value.__enter__.return_value
    user_dao_mock.create_user.side_effect = IntegrityError(None, None, None)

    await save_user(mock_message, mock_fsm)

    # Verify bot response
    mock_message.reply.assert_called_once_with("Ошибка сохранения пользователя в БД")
