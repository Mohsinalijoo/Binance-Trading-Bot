"""Application configuration loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


DEFAULT_BASE_URL = "https://testnet.binancefuture.com"


@dataclass(frozen=True)
class Settings:
    api_key: str
    api_secret: str
    base_url: str = DEFAULT_BASE_URL
    recv_window: int = 5000
    timeout: int = 10


def load_settings(base_url_override: str | None = None) -> Settings:
    api_key = os.getenv("BINANCE_API_KEY", "").strip()
    api_secret = os.getenv("BINANCE_API_SECRET", "").strip()
    base_url = (base_url_override or os.getenv("BINANCE_BASE_URL") or DEFAULT_BASE_URL).strip()
    recv_window = int(os.getenv("BINANCE_RECV_WINDOW", "5000"))
    timeout = int(os.getenv("BINANCE_HTTP_TIMEOUT", "10"))

    if not api_key or not api_secret:
        raise ValueError(
            "Missing BINANCE_API_KEY or BINANCE_API_SECRET. "
            "Create a .env file from .env.example and add your Futures Testnet keys."
        )

    return Settings(
        api_key=api_key,
        api_secret=api_secret,
        base_url=base_url.rstrip("/"),
        recv_window=recv_window,
        timeout=timeout,
    )


def load_env_file(path: str = ".env") -> None:
    env_path = Path(path)
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)
