"""Тесты для обработки команд."""

from unittest.mock import MagicMock

from src.bot.commands import list_players, process_command
from src.bot.rcon import RCONClient


def test_list_players(mocker):
    mock_rcon = MagicMock(spec=RCONClient)
    mock_rcon.send_command.return_value = "There are 2 of a max of 20 players online: Steve, Alex"
    players = list_players(mock_rcon)
    assert players == ["Steve", "Alex"]
    mock_rcon.send_command.assert_called_with("list")


def test_process_command_list(mocker):
    mock_rcon = MagicMock()
    mock_rcon.send_command.return_value = "online: Alice"
    # подменим save_players_to_cache, чтобы не писать в файл
    mocker.patch("src.bot.commands.save_players_to_cache")
    result = process_command(mock_rcon, "!list")
    assert "Alice" in result


def test_process_command_say():
    mock_rcon = MagicMock()
    result = process_command(mock_rcon, "!say Hello world")
    assert "Message sent" in result
    mock_rcon.send_command.assert_called_with("say Hello world")


def test_process_command_unknown():
    mock_rcon = MagicMock()
    result = process_command(mock_rcon, "!unknown")
    assert "Unknown command" in result
