#!/usr/bin/env python3
"""Точка входа в бота."""

import sys
from pathlib import Path

# Добавляем корень проекта в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.bot.commands import process_command
from src.bot.rcon import RCONClient
from src.utils.config import config
from src.utils.logger import setup_logger


def main():
    logger = setup_logger()
    logger.info("Minecraft Bot starting...")

    rcon = RCONClient(
        host=config["rcon_host"],
        port=config["rcon_port"],
        password=config["rcon_password"],
    )

    try:
        rcon.connect()
        logger.info("Connected to RCON")

        # Простейший цикл чтения команд из stdin
        print("Bot ready. Type commands (e.g. '!list', '!say Hello'):")
        while True:
            raw = input("> ").strip()
            if raw.lower() in ("exit", "quit"):
                break
            if raw.startswith("!"):
                response = process_command(rcon, raw)
                print(response)
            else:
                print("Unknown command. Use !help")
    except KeyboardInterrupt:
        logger.info("Shutting down")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        rcon.disconnect()


if __name__ == "__main__":
    main()
