# clients/arcade/replay_api_client.py

import requests


class ReplayAPIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.timeout = 0.5

    # -------------------------
    # Internal helper
    # -------------------------
    def _safe_json(self, response):
        if response.status_code != 200:
            raise RuntimeError(
                f"HTTP {response.status_code}: {response.text}"
            )

        if not response.content:
            raise RuntimeError("Empty response body")

        return response.json()

    # -------------------------
    # Clock
    # -------------------------
    def get_clock_state(self):
        r = requests.get(
            f"{self.base_url}/clock/state",
            timeout=self.timeout,
        )
        return self._safe_json(r)

    def play(self):
        r = requests.post(
            f"{self.base_url}/clock/play",
            timeout=self.timeout,
        )
        return self._safe_json(r)

    def pause(self):
        r = requests.post(
            f"{self.base_url}/clock/pause",
            timeout=self.timeout,
        )
        return self._safe_json(r)

    def reset(self):
        r = requests.post(
            f"{self.base_url}/clock/reset",
            timeout=self.timeout,
        )
        return self._safe_json(r)

    def tick(self, delta_ms: int = 1000):
        r = requests.post(
            f"{self.base_url}/clock/tick",
            params={"base_ms": delta_ms},
            timeout=self.timeout,
        )
        return self._safe_json(r)

    def seek(self, target_time_ms: int):
        r = requests.post(
            f"{self.base_url}/clock/seek",
            params={"target_time_ms": target_time_ms},
            timeout=self.timeout,
        )
        return self._safe_json(r)

    # -------------------------
    # Frames
    # -------------------------
    def get_frame(self):
        r = requests.get(
            f"{self.base_url}/replay/frame",
            timeout=self.timeout,
        )
        return self._safe_json(r)
