from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message


@pytest.fixture
def mocked_db():
    with patch("bot.database.db.get_db") as mocked_db:
        db_session = MagicMock()
        mocked_db.return_value = db_session
        yield db_session


@pytest.fixture
def mocked_scribe_root_me():
    with patch("bot.utils.root_me.scribe_root_me", return_value="mocked_nickname"):
        yield


@pytest.fixture
def mock_message():
    message = AsyncMock(spec=Message)
    message.text = ""
    return message


@pytest.fixture
def mock_fsm():
    return FSMContext(
        storage=MemoryStorage(),
        key=("chat_id", "user_id"),
    )
