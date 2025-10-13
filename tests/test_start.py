import pytest
from aiogram.fsm.context import FSMContext
from unittest.mock import patch
from sqlalchemy.exc import IntegrityError

from bot.handlers.start import cmd_start, get_fullname, save_user


@pytest.mark.asyncio
async def test_cmd_start(mock_message, mock_fsm: FSMContext):
    mock_message.text = "/start"
    # pass user=None to simulate unregistered user
    await cmd_start(mock_message, mock_fsm, None)

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
    # from_user provided by fixture

    await mock_fsm.set_data({"full_name": "John Doe"})
    # Patch UserDAO used in handler to use our mocked DB session
    with patch("bot.handlers.start.UserDAO") as MockUserDAO:
        MockUserDAO.return_value.create_user.return_value = None
        await save_user(mock_message, mock_fsm)

        # Verify user creation in DB
        MockUserDAO.return_value.create_user.assert_called_once()

    # Verify bot response
    mock_message.answer.assert_called()


@pytest.mark.asyncio
async def test_save_user_integrity_error(
    mock_message, mock_fsm: FSMContext, mocked_db, mocked_scribe_root_me
):
    mock_message.text = "https://www.root-me.org/user"

    await mock_fsm.set_data({"full_name": "John Doe"})
    with patch("bot.handlers.start.UserDAO") as MockUserDAO:
        MockUserDAO.return_value.create_user.side_effect = IntegrityError(None, None, None)
        await save_user(mock_message, mock_fsm)

    # Verify bot response
    mock_message.reply.assert_called_once()
