from unittest.mock import MagicMock

from loader import load_player_month


def test_load_player_month_idempotent(monkeypatch):
    monkeypatch.setenv("CHESS_API_USER_AGENT", "test-agent test@test.com")

    fake_client = MagicMock()
    fake_client.get_games.return_value = {"games": [{"url": "test", "rated": True}]}

    fake_db_conn = MagicMock()

    load_player_month(fake_client, fake_db_conn, "magnuscarlsen", 2024, 3, "test_01")
    load_player_month(fake_client, fake_db_conn, "magnuscarlsen", 2024, 3, "test_02")

    mock_cursor = fake_db_conn.cursor.return_value.__enter__.return_value

    first_call = mock_cursor.execute.call_args_list[0]
    second_call = mock_cursor.execute.call_args_list[1]

    first_params = first_call.args[1]
    second_params = second_call.args[1]

    assert first_params[0] == second_params[0]  # username совпадает
    assert first_params[1] == second_params[1]  # archive_month совпадает
