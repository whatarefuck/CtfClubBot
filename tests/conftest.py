from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from types import SimpleNamespace
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message


@pytest.fixture
def mocked_db():
    # Patch the get_db import used by handlers (they import from `database.db`)
    with patch("database.db.get_db") as mocked_db:
        db_session = MagicMock()
        # Make the returned object act as a context manager
        mocked_db.return_value.__enter__.return_value = db_session
        mocked_db.return_value.__exit__.return_value = None
        yield mocked_db


@pytest.fixture
def mocked_scribe_root_me():
    with patch("utils.root_me.scribe_root_me", return_value="mocked_nickname"):
        yield


@pytest.fixture
def mock_message():
    message = AsyncMock(spec=Message)
    message.text = ""
    # Ensure answer/reply are awaitable
    message.answer = AsyncMock()
    message.reply = AsyncMock()
    # Provide a simple from_user object commonly accessed in handlers
    message.from_user = SimpleNamespace(id=123, username="test_user")
    return message


@pytest.fixture
def mock_fsm():
    return FSMContext(
        storage=MemoryStorage(),
        key=("chat_id", "user_id"),
    )
