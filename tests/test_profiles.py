import pytest
from types import SimpleNamespace

from bot.handlers.profiles import my_profile_handler


@pytest.mark.asyncio
async def test_my_profile_complete(mock_message):
    user = SimpleNamespace(full_name="John Doe", root_me_nickname="jdoe", lives=3, points=7)
    await my_profile_handler(mock_message, user)

    # Ensure reply called with formatted profile containing fields
    mock_message.reply.assert_called_once()
    called_arg = mock_message.reply.call_args.args[0]
    assert "Полное имя: John Doe" in called_arg
    assert "RootMe ник: jdoe" in called_arg
    assert "Очки: 7" in called_arg


@pytest.mark.asyncio
async def test_my_profile_missing_fields(mock_message):
    user = SimpleNamespace(full_name=None, root_me_nickname=None, lives=3, points=0)
    await my_profile_handler(mock_message, user)

    mock_message.reply.assert_called_once()
    called_arg = mock_message.reply.call_args.args[0]
    assert "Полное имя: Не указано" in called_arg
    assert "RootMe ник: Не указано" in called_arg
