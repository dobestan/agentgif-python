"""Configuration storage — ~/.config/agentgif/config.json."""

import json
from pathlib import Path
from typing import Any

CONFIG_DIR = Path.home() / ".config" / "agentgif"
CONFIG_FILE = CONFIG_DIR / "config.json"
DEFAULT_BASE_URL = "https://agentgif.com"


def _load() -> dict[str, Any]:
    if CONFIG_FILE.exists():
        result: dict[str, Any] = json.loads(CONFIG_FILE.read_text())
        return result
    return {}


def _save(data: dict[str, Any]) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(data, indent=2))


def get_api_key() -> str | None:
    return _load().get("api_key")


def get_base_url() -> str:
    url: str = _load().get("base_url", DEFAULT_BASE_URL)
    return url


def set_credentials(api_key: str, username: str) -> None:
    data = _load()
    data["api_key"] = api_key
    data["username"] = username
    _save(data)


def get_username() -> str | None:
    return _load().get("username")


def clear_credentials() -> None:
    data = _load()
    data.pop("api_key", None)
    data.pop("username", None)
    _save(data)
