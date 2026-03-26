import pytest
import os
import csv
import requests
from unittest.mock import patch, MagicMock
from app.tasks import master_fetch_task, save_chunk_to_csv

MOCK_USERS = [
    {"id": 1, "name": "User 1", "email": "u1@test.com"},
    {"id": 2, "name": "User 2", "email": "u2@test.com"},
    {"id": 3, "name": "User 3", "email": "u3@test.com"},
]


@patch("app.tasks.requests.get")
@patch("app.tasks.save_chunk_to_csv.delay")
def test_master_fetch_task(mock_delay, mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = MOCK_USERS
    mock_get.return_value = mock_response

    with patch("app.tasks.CHUNK_SIZE", 2):
        result = master_fetch_task()

    assert "Dispatched 2 chunk tasks" in result
    assert mock_get.called

    assert mock_delay.call_count == 2

    with open("users_data.csv", "r") as f:
        reader = csv.reader(f)
        header = next(reader)
        assert header == ["id", "name", "email"]


def test_save_chunk_to_csv():
    chunk = [MOCK_USERS[0]]

    if os.path.exists("users_data.csv"):
        os.remove("users_data.csv")

    result = save_chunk_to_csv(chunk)

    assert "Saved 1 users" in result

    with open("users_data.csv", "r") as f:
        lines = f.readlines()
        assert "1,User 1,u1@test.com" in lines[0]


@patch("app.tasks.requests.get")
def test_master_fetch_api_timeout(mock_get):
    mock_get.side_effect = requests.exceptions.Timeout("Connection timed out")

    with pytest.raises(requests.exceptions.Timeout):
        master_fetch_task()


@patch("app.tasks.requests.get")
def test_master_fetch_invalid_json(mock_get):
    mock_response = MagicMock()
    mock_response.json.side_effect = ValueError("No JSON object could be decoded")
    mock_get.return_value = mock_response

    with pytest.raises(ValueError, match="No JSON object could be decoded"):
        master_fetch_task()


@patch("app.tasks.requests.get")
@patch("app.tasks.open", side_effect=PermissionError("Permission denied"))
def test_master_fetch_file_permission_error(mock_open, mock_get):
    mock_get.return_value.json.return_value = [{"id": 1, "name": "Test"}]

    with pytest.raises(PermissionError):
        master_fetch_task()


def test_save_chunk_with_corrupted_data():
    bad_chunk = [{"id": 1, "wrong_key": "No Name"}]

    with pytest.raises(KeyError):
        save_chunk_to_csv(bad_chunk)


def test_save_chunk_not_iterable():
    with pytest.raises(TypeError):
        save_chunk_to_csv(None)