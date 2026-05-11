"""Тесты для RCON клиента (мок соединения)."""

import socket
from unittest.mock import MagicMock, patch

import pytest

from src.bot.rcon import RCONClient


@patch("socket.socket")
def test_connect_auth(mock_socket):
    mock_sock = MagicMock()
    mock_socket.return_value = mock_sock
    # Имитируем успешный ответ от сервера
    mock_sock.recv.side_effect = [
        b"\x0a\x00\x00\x00",   # длина 10
        b"\x00\x00\x00\x00\x03\x00\x00\x00\x00\x00",  # request_id=0, type=3, пустое тело
    ]

    client = RCONClient("localhost", 25575, "pass")
    client.connect()
    mock_sock.connect.assert_called_with(("localhost", 25575))
    # Проверяем, что отправили логин
    mock_sock.send.assert_called()
    assert client.sock is not None
    client.disconnect()
    mock_sock.close.assert_called()
