import pytest
from types import SimpleNamespace

from bot.handlers.leaderboard import (
    format_top_rating,
    format_user_status,
    leaderboard_handler,
)
from unittest.mock import patch


def make_user(id, username, points):
    return SimpleNamespace(id=id, username=username, points=points)


def test_format_top_rating_empty():
    msgs = format_top_rating([])
    assert msgs[0].startswith("🏆")
    assert "Пока что никто" in msgs[1]


def test_format_top_rating_nonempty():
    users = [make_user(1, "u1", 10), make_user(2, "u2", 8)]
    msgs = format_top_rating(users)
    assert "1. @u1 — 10 баллов" in msgs[1]
    assert "2. @u2 — 8 баллов" in msgs[2]


def test_format_user_status_in_top():
    top = [make_user(1, "u1", 10), make_user(2, "u2", 5)]
    user = make_user(2, "u2", 5)
    msgs = format_user_status(user, top)
    assert "Ваш статус" in msgs[0]
    assert any("Вы на" in m for m in msgs)


def test_format_user_status_not_in_top_zero_points():
    top = [make_user(1, "u1", 10)]
    user = make_user(2, "u2", 0)
    msgs = format_user_status(user, top)
    assert "У вас пока нет баллов" in msgs[1]


def test_format_user_status_not_in_top_needs_points():
    top = [make_user(i, f"u{i}", pts) for i, pts in enumerate(range(20, 0, -1), start=1)]
    # last top score is 1; user has some points but not enough
    user = make_user(999, "new", 1)
    msgs = format_user_status(user, top)
    assert "Чтобы войти в топ-20" in msgs[1]


@pytest.mark.asyncio
async def test_leaderboard_handler(mock_message, mocked_db):
    user1 = SimpleNamespace(id=1, username="u1", points=10)
    user2 = SimpleNamespace(id=2, username="u2", points=5)
    # Patch UserDAO class used inside the handler module
    with patch("bot.handlers.leaderboard.UserDAO") as MockUserDAO:
        MockUserDAO.return_value.leaderboard.return_value = [user1, user2]
        user = SimpleNamespace(id=3, username="me", points=0)
        await leaderboard_handler(mock_message, user)

    # Ensure answer called at least once
    mock_message.answer.assert_called()
