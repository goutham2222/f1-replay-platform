from __future__ import annotations

import requests


class ReplayAPIClient:
    """
    Thin HTTP client over the Replay API.
    Keep it small + predictable.
    """

    def __init__(self, base_url: str, timeout_s: float = 0.5):
        self.base_url = base_url.rstrip("/")
        self.timeout_s = timeout_s
        self.session = requests.Session()

    def get_frame(self) -> dict:
        resp = self.session.get(
            f"{self.base_url}/replay/frame",
            timeout=self.timeout_s,
        )
        resp.raise_for_status()
        return resp.json()

    def tick(self, base_ms: int = 1000) -> dict:
        """
        Optional helper if you want the client to drive time.
        Not required for story 58.
        """
        resp = self.session.post(
            f"{self.base_url}/clock/tick",
            params={"base_ms": base_ms},
            timeout=self.timeout_s,
        )
        resp.raise_for_status()
        return resp.json()
