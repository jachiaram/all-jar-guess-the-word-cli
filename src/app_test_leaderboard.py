import json
import threading
from http.client import HTTPConnection
from http.server import HTTPServer

import pytest

from app import RequestHandler
from leaderboard_service import get_leaderboard_data


# --- Unit tests for response data ---


def test_leaderboard_returns_players_with_stats(player_factory):
    players = [
        player_factory(name="Alice", wins=4, losses=5, guess_count=10),
        player_factory(name="Tom", wins=3, losses=12, guess_count=13),
    ]

    result = get_leaderboard_data(players)

    assert result == {
        "players": [
            {"name": "Alice", "wins": 4, "losses": 5, "averageGuesses": 2.5},
            {"name": "Tom", "wins": 3, "losses": 12, "averageGuesses": 4.3},
        ]
    }


def test_leaderboard_sorted_by_wins_descending(player_factory):
    players = [
        player_factory(name="Alice", wins=4, losses=5, guess_count=0),
        player_factory(name="Bob", wins=8, losses=2, guess_count=0),
        player_factory(name="Charlie", wins=2, losses=10, guess_count=0),
    ]

    result = get_leaderboard_data(players)

    assert [p["name"] for p in result["players"]] == ["Bob", "Alice", "Charlie"]


def test_leaderboard_average_guesses_uses_wins_only(player_factory):
    players = [
        player_factory(name="Diana", wins=2, losses=1, guess_count=7),
    ]

    result = get_leaderboard_data(players)

    assert result["players"][0]["averageGuesses"] == 3.5


def test_leaderboard_empty(player_factory):
    result = get_leaderboard_data([])

    assert result == {"players": []}


# --- Integration tests for HTTP endpoint ---


@pytest.fixture(scope="module")
def server():
    httpd = HTTPServer(("127.0.0.1", 0), RequestHandler)
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever)
    thread.daemon = True
    thread.start()
    yield port
    httpd.shutdown()


def _get(port, path):
    conn = HTTPConnection("127.0.0.1", port)
    conn.request("GET", path)
    response = conn.getresponse()
    body = response.read()
    headers = dict(response.getheaders())
    conn.close()
    return response.status, json.loads(body), headers


def test_leaderboard_endpoint_returns_200(server, monkeypatch):
    monkeypatch.setattr("app.load_players", lambda: [])
    status, body, headers = _get(server, "/leaderboard")
    assert status == 200
    assert body == {"players": []}
    assert headers.get("Content-Type") == "application/json"


def test_leaderboard_endpoint_returns_players(server, player_factory, monkeypatch):
    players = [
        player_factory(name="Alice", wins=4, losses=5, guess_count=10),
        player_factory(name="Tom", wins=3, losses=12, guess_count=13),
    ]
    monkeypatch.setattr("app.load_players", lambda: players)

    status, body, _ = _get(server, "/leaderboard")

    assert status == 200
    assert body["players"][0]["name"] == "Alice"
    assert body["players"][1]["name"] == "Tom"
