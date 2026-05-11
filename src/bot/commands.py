"""Обработка игровых команд бота."""

import json
from pathlib import Path
from typing import List

from src.bot.rcon import RCONClient

# Путь к файлу кэша игроков (data/players.json)
PLAYERS_CACHE_PATH = Path(__file__).parent.parent.parent / "data" / "players.json"


def list_players(rcon: RCONClient) -> List[str]:
    """Получить список игроков онлайн через команду /list."""
    response = rcon.send_command("list")
    # Ответ Minecraft: "There are 2 of a max of 20 players online: Alice, Bob"
    if ":" in response:
        players_part = response.split(":")[-1].strip()
        if players_part:
            return [p.strip() for p in players_part.split(",")]
    return []


def say(rcon: RCONClient, message: str) -> str:
    """Отправить сообщение в чат."""
    rcon.send_command(f'say {message}')
    return f"Message sent: {message}"


def save_players_to_cache(players: List[str]):
    """Сохранить список игроков в JSON кэш (например, для статистики)."""
    PLAYERS_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    cache = {"last_update": str(__import__("datetime").datetime.now()), "players": players}
    with open(PLAYERS_CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2)


def process_command(rcon: RCONClient, command_line: str) -> str:
    """Разобрать команду бота (с префиксом !) и выполнить."""
    if not command_line.startswith("!"):
        return "Unknown command. Use !list, !say <text>, !help"

    parts = command_line[1:].split(maxsplit=1)
    cmd = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""

    if cmd == "list":
        players = list_players(rcon)
        save_players_to_cache(players)
        if players:
            return f"Online players: {', '.join(players)}"
        else:
            return "No players online."
    elif cmd == "say":
        if not args:
            return "Usage: !say <message>"
        return say(rcon, args)
    elif cmd == "backup":
        # Простой вызов команды сервера (требуется плагин или скрипт)
        rcon.send_command("save-off")
        rcon.send_command("save-all")
        response = rcon.send_command("backup start")  # если есть плагин
        rcon.send_command("save-on")
        return response or "Backup initiated (check logs)."
    elif cmd == "help":
        return "Commands: !list, !say <text>, !backup"
    else:
        return f"Unknown command '{cmd}'. Type !help."
