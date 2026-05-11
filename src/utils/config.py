"""Загрузка конфигурации из .env или config.yml."""

import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

# Загружаем .env (приоритет выше)
dotenv_path = Path(__file__).parent.parent.parent / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path)

# Загружаем config.yml как fallback
config_path = Path(__file__).parent.parent.parent / "config.yml"
yaml_config = {}
if config_path.exists():
    with open(config_path, "r") as f:
        yaml_config = yaml.safe_load(f) or {}

# Собираем финальный конфиг с приоритетом переменных окружения
config = {
    "rcon_host": os.getenv("RCON_HOST", yaml_config.get("rcon", {}).get("host", "127.0.0.1")),
    "rcon_port": int(os.getenv("RCON_PORT", yaml_config.get("rcon", {}).get("port", 25575))),
    "rcon_password": os.getenv("RCON_PASSWORD", yaml_config.get("rcon", {}).get("password", "")),
}
