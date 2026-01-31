from dataclasses import dataclass
import os

try:
    # Optional; safe if not installed
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass


def _env_int(key: str, default: int) -> int:
    v = os.getenv(key)
    return default if v is None or v.strip() == "" else int(v)


def _env_str(key: str, default: str) -> str:
    v = os.getenv(key)
    return default if v is None or v.strip() == "" else v


@dataclass(frozen=True)
class Settings:
    # Window
    WINDOW_WIDTH: int = _env_int("ARCADE_WINDOW_WIDTH", 1400)
    WINDOW_HEIGHT: int = _env_int("ARCADE_WINDOW_HEIGHT", 800)
    WINDOW_TITLE: str = _env_str("ARCADE_WINDOW_TITLE", "F1 Replay Platform — Arcade Client")

    # Replay API
    REPLAY_API_BASE_URL: str = _env_str("REPLAY_API_BASE_URL", "http://localhost:8000")

    # S3 curated dataset
    CURATED_BUCKET: str = _env_str("CURATED_BUCKET", "f1-replay-curated-goutham")
    SEASON: int = _env_int("SEASON", 2023)
    ROUND: int = _env_int("ROUND", 1)


settings = Settings()
