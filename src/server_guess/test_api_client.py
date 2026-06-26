import json
from unittest.mock import patch, MagicMock

import pytest
import requests

from . import api_client


def test_get_player_id_when_session_file_missing(capsys, tmp_path):
    with patch.object(api_client, "SESSION_FILE", str(tmp_path / "nonexistent.json")):
        with pytest.raises(SystemExit) as exc:
            api_client.get_player_id()

    assert exc.value.code == 1
    assert "Please login to continue" in capsys.readouterr().out


def test_get_player_id_when_player_id_absent_in_session(capsys, tmp_path):
    session_file = tmp_path / "session.json"
    session_file.write_text(json.dumps({}))

    with patch.object(api_client, "SESSION_FILE", str(session_file)):
        with pytest.raises(SystemExit) as exc:
            api_client.get_player_id()

    assert exc.value.code == 1
    assert "Please login to continue" in capsys.readouterr().out


def test_get_player_id_returns_stored_id(tmp_path):
    session_file = tmp_path / "session.json"
    session_file.write_text(json.dumps({"player_id": "7"}))

    with patch.object(api_client, "SESSION_FILE", str(session_file)):
        player_id = api_client.get_player_id()

    assert player_id == "7"


def test_post_guess_server_down_shows_friendly_message(capsys):
    with patch("requests.post", side_effect=requests.exceptions.ConnectionError):
        with pytest.raises(SystemExit) as exc:
            api_client.post_guess("7", "crane")

    assert exc.value.code == 1
    assert "Looks like the wurdal servers are taking a loss... try again later!" in capsys.readouterr().out


def test_post_guess_wrong_length_prints_server_error(capsys):
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.json.return_value = {"error": "Guess must be exactly 5 letters"}

    with patch("requests.post", return_value=mock_response):
        with pytest.raises(SystemExit) as exc:
            api_client.post_guess("7", "cat")

    assert exc.value.code == 1
    assert "Guess must be exactly 5 letters" in capsys.readouterr().out


def test_post_guess_sends_correct_request():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "guesses": [{"guess": "crane", "colors": {"0": "green", "1": "grey", "2": "grey", "3": "grey", "4": "grey"}}],
        "word_length": 5,
        "won": False,
        "lost": False,
    }

    with patch("requests.post", return_value=mock_response) as mock_post:
        api_client.post_guess("7", "crane")

    mock_post.assert_called_once_with(
        "http://localhost:8000/players/7/guess",
        json={"guess": "crane"},
        headers={"Authorization": "Bearer 7"},
    )


def test_post_guess_returns_response_on_success():
    expected = {
        "guesses": [{"guess": "crane", "colors": {"0": "green", "1": "grey", "2": "grey", "3": "grey", "4": "grey"}}],
        "word_length": 5,
        "won": False,
        "lost": False,
    }
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = expected

    with patch("requests.post", return_value=mock_response):
        result = api_client.post_guess("7", "crane")

    assert result == expected


def test_post_guess_winning_response_includes_won_flag():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "guesses": [{"guess": "crane", "colors": {str(i): "green" for i in range(5)}}],
        "word_length": 5,
        "won": True,
        "lost": False,
    }

    with patch("requests.post", return_value=mock_response):
        result = api_client.post_guess("7", "crane")

    assert result["won"] is True


def test_post_guess_losing_response_includes_word():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "guesses": [{"guess": "zzzzz", "colors": {str(i): "grey" for i in range(5)}}],
        "word_length": 5,
        "won": False,
        "lost": True,
        "word": "crane",
    }

    with patch("requests.post", return_value=mock_response):
        result = api_client.post_guess("7", "zzzzz")

    assert result["lost"] is True
    assert result["word"] == "crane"
