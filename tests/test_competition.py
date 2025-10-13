import pytest
from aiogram.fsm.context import FSMContext

from bot.handlers.competition import cmd_start as competition_cmd_start


@pytest.mark.asyncio
async def test_competition_cmd_start(mock_message, mock_fsm: FSMContext):
    mock_message.text = "/add_competition"
    # pass a dummy user (not used in handler)
    await competition_cmd_start(mock_message, mock_fsm)

    # Verify bot response
    mock_message.answer.assert_called_once_with("Название мероприятия.")

    # Verify state transition
    assert await mock_fsm.get_state() == "CompetitionForm:name"
