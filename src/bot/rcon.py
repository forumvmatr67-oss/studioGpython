"""RCON клиент для Minecraft сервера."""

import socket
import struct
import time
from typing import Optional

PACKET_TYPE_COMMAND = 2
PACKET_TYPE_LOGIN = 3


class RCONClient:
    def __init__(self, host: str, port: int, password: str):
        self.host = host
        self.port = port
        self.password = password
        self.sock: Optional[socket.socket] = None
        self.request_id = 0

    def _send_packet(self, packet_type: int, body: str) -> Optional[int]:
        """Отправить пакет RCON и вернуть request ID."""
        if not self.sock:
            raise ConnectionError("Not connected")
        body_bytes = body.encode("utf-8")
        # длина = длина тела + 2 байта (тип и ID) + нуль-терминатор? реально +10
        # Формат пакета: length (int32) + request_id (int32) + type (int32) + body (байты) + нулевой байт + нулевой байт
        length = 10 + len(body_bytes)  # 4+4+2 + len
        packet = struct.pack("<iii", length - 4, self.request_id, packet_type) + body_bytes + b"\x00\x00"
        self.sock.send(packet)
        self.request_id += 1
        return self.request_id - 1

    def _receive_packet(self) -> Optional[tuple]:
        """Принять и распарсить ответный пакет. Возвращает (request_id, type, body)."""
        if not self.sock:
            return None
        # длина пакета (первые 4 байта)
        raw_len = self.sock.recv(4)
        if len(raw_len) < 4:
            return None
        length = struct.unpack("<i", raw_len)[0]
        # читаем оставшиеся length байт
        data = self.sock.recv(length)
        request_id, packet_type = struct.unpack("<ii", data[:8])
        body = data[8:-2].decode("utf-8", errors="replace")
        return (request_id, packet_type, body)

    def connect(self):
        """Соединение и аутентификация."""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self._send_packet(PACKET_TYPE_LOGIN, self.password)
        resp = self._receive_packet()
        if resp and resp[1] == PACKET_TYPE_LOGIN and resp[0] == 0:
            # request_id -1 означает неудачу
            if resp[0] == -1:
                raise ConnectionError("RCON authentication failed")
        else:
            raise ConnectionError("RCON login error")

    def disconnect(self):
        if self.sock:
            self.sock.close()
            self.sock = None

    def send_command(self, command: str) -> str:
        """Отправить команду на сервер и вернуть ответ."""
        if not self.sock:
            raise ConnectionError("Not connected")
        self._send_packet(PACKET_TYPE_COMMAND, command)
        # Получаем ответ (может быть несколько пакетов)
        result = []
        while True:
            resp = self._receive_packet()
            if not resp or resp[1] != PACKET_TYPE_COMMAND:
                break
            result.append(resp[2])
            # маленькая задержка, чтобы собрать все части
            time.sleep(0.02)
        return "\n".join(result)
