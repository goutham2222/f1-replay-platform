from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass(frozen=True)
class ArcadeConfig:
    """
    Immutable configuration for the Arcade visualization client.

    Rules:
    - Loaded once at startup
    - No runtime mutation
    - No replay logic here
    """

    replay_api_base_url: str
    window_width: int
    window_height: int
    window_title: str


def load_config() -> ArcadeConfig:
    """
    Load configuration from environment variables.

    Priority:
    1. clients/arcade/.env (if present)
    2. Process environment

    Required:
    - REPLAY_API_BASE_URL
    """

    # Load .env if it exists (safe no-op otherwise)
    load_dotenv()

    replay_api_base_url = os.getenv("REPLAY_API_BASE_URL")
    if not replay_api_base_url:
        raise RuntimeError(
            "REPLAY_API_BASE_URL is required. "
            "Set it in clients/arcade/.env or as an environment variable."
        )

    replay_api_base_url = replay_api_base_url.rstrip("/")

    window_width = int(os.getenv("ARCADE_WINDOW_WIDTH", "1280"))
    window_height = int(os.getenv("ARCADE_WINDOW_HEIGHT", "720"))
    window_title = os.getenv(
        "ARCADE_WINDOW_TITLE",
        "F1 Replay Platform — Arcade Client",
    )

    return ArcadeConfig(
        replay_api_base_url=replay_api_base_url,
        window_width=window_width,
        window_height=window_height,
        window_title=window_title,
    )
