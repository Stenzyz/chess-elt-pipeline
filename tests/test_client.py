import httpx
import pytest
import respx
import tenacity
from client import ApiClient


@respx.mock
def test_get_titled_success(monkeypatch):
    monkeypatch.setenv("CHESS_API_USER_AGENT", "test-agent test@test.com")

    Route = respx.get("https://api.chess.com/pub/titled/GM").mock(
        return_value=httpx.Response(200, json={"players": ["magnuscarlsen"]})
    )

    client = ApiClient()
    data = client.get_titled("GM")

    assert Route.called
    assert data == {"players": ["magnuscarlsen"]}


@respx.mock
def test_get_archives_success(monkeypatch):
    monkeypatch.setenv("CHESS_API_USER_AGENT", "test-agent test@test.com")

    Route = respx.get(
        "https://api.chess.com/pub/player/magnuscarlsen/games/archives"
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                "archives": [
                    "https://api.chess.com/pub/player/magnuscarlsen/games/2026/05"
                ]
            },
        )
    )

    client = ApiClient()
    data = client.get_archives("magnuscarlsen")

    assert Route.called
    assert data == {
        "archives": ["https://api.chess.com/pub/player/magnuscarlsen/games/2026/05"]
    }


@respx.mock
def test_get_stats_success(monkeypatch):
    monkeypatch.setenv("CHESS_API_USER_AGENT", "test-agent test@test.com")

    Route = respx.get("https://api.chess.com/pub/player/magnuscarlsen/stats").mock(
        return_value=httpx.Response(
            200,
            json={
                "chess_rapid": {"last": {"rating": 2912, "date": 1781347004, "rd": 48}}
            },
        )
    )

    client = ApiClient()
    data = client.get_stats("magnuscarlsen")

    assert Route.called
    assert data == {
        "chess_rapid": {"last": {"rating": 2912, "date": 1781347004, "rd": 48}}
    }


@respx.mock
def test_get_games_success(monkeypatch):
    monkeypatch.setenv("CHESS_API_USER_AGENT", "test-agent test@test.com")

    Route = respx.get(
        "https://api.chess.com/pub/player/magnuscarlsen/games/2026/05"
    ).mock(
        return_value=httpx.Response(
            200, json={"games": [{"url": "https://example.com/game/1", "rated": True}]}
        )
    )

    client = ApiClient()
    data = client.get_games("magnuscarlsen", 2026, 5)

    assert Route.called
    assert data == {"games": [{"url": "https://example.com/game/1", "rated": True}]}


@respx.mock
def test_404_no_retry(monkeypatch):
    monkeypatch.setenv("CHESS_API_USER_AGENT", "test-agent test@test.com")

    Route = respx.get("https://api.chess.com/pub/titled/GM").mock(
        return_value=httpx.Response(404, json={})
    )

    client = ApiClient()

    with pytest.raises(httpx.HTTPStatusError):
        client.get_titled("GM")
    assert Route.call_count == 1


@respx.mock
def test_get_retry_success(monkeypatch):
    monkeypatch.setenv("CHESS_API_USER_AGENT", "test-agent test@test.com")

    Route = respx.get("https://api.chess.com/pub/titled/GM").mock(
        return_value=httpx.Response(429, json={})
    )

    client = ApiClient()

    with pytest.raises(tenacity.RetryError):
        client.get_titled("GM")
    assert Route.call_count == 5
