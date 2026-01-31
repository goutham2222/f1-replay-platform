from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict
import requests


@dataclass(frozen=True)
class ReplayApiClient:
    """
    Thin, stateless HTTP client for the Replay API.

    Rules:
    - No replay logic
    - No caching
    - No background threads
    - Pure request → response
    """

    base_url: str
    timeout_seconds: float = 5.0

    def get_clock_state(self) -> Dict[str, Any]:
        """
        GET /clock/state
        """
        return self._get("/clock/state")

    def tick_clock(self) -> Dict[str, Any]:
        """
        POST /clock/tick
        """
        return self._post("/clock/tick")

    def seek_clock(self, target_time_ms: int) -> Dict[str, Any]:
        """
        POST /clock/seek
        """
        return self._post(
            "/clock/seek",
            json={"target_time_ms": target_time_ms},
        )

    def reset_clock(self) -> Dict[str, Any]:
        """
        POST /clock/reset
        """
        return self._post("/clock/reset")

    def get_replay_frame(self) -> Dict[str, Any]:
        """
        GET /replay/frame
        """
        return self._get("/replay/frame")

    # -------------------------
    # Internal helpers
    # -------------------------

    def _get(self, path: str) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        response = requests.get(url, timeout=self.timeout_seconds)
        response.raise_for_status()
        return response.json()

    def _post(self, path: str, json: Dict[str, Any] | None = None) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        response = requests.post(url, json=json, timeout=self.timeout_seconds)
        response.raise_for_status()
        return response.json()
