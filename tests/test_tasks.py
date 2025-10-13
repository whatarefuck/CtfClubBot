import pytest
from types import SimpleNamespace

from bot.handlers.tasks import my_tasks_handler
from unittest.mock import patch


@pytest.mark.asyncio
async def test_my_tasks_no_tasks(mock_message, mocked_db):
    # Setup: TaskDao.user_tasks returns empty list
    # Patch the TaskDao used in the handler module to return empty list
    with patch("bot.handlers.tasks.TaskDao") as MockTaskDao:
        MockTaskDao.return_value.user_tasks.return_value = []
        user = SimpleNamespace(id=1, username="test_user", points=0)
        await my_tasks_handler(mock_message, user)

    # Expect a reply indicating no tasks
    mock_message.reply.assert_called_once_with("Пока нет никаких задач.")


@pytest.mark.asyncio
async def test_my_tasks_with_tasks(mock_message, mocked_db):
    # Create a fake task object similar to database.models.Task
    fake_task = SimpleNamespace(name="Task1", description="Desc", url="http://u")

    # Mock the DAO to return one task
    with patch("bot.handlers.tasks.TaskDao") as MockTaskDao:
        MockTaskDao.return_value.user_tasks.return_value = [fake_task]
        user = SimpleNamespace(id=1, username="test_user", points=0)
        await my_tasks_handler(mock_message, user)

    expected_text = (
        "Задача: Task1\nОписание: Desc\nСсылка: http://u\n\n"
    )
    mock_message.reply.assert_called_once_with(expected_text)
