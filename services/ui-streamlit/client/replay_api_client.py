import requests
from typing import Dict, Any, Optional


class ReplayApiClient:
    def __init__(self, base_url: str, timeout: float = 10.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _get(self, path: str) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        r = requests.get(url, timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def _post(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        r = requests.post(url, params=params, timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    # -------- Clock APIs (MATCH replay-api EXACTLY) --------

    def get_clock_state(self) -> Dict[str, Any]:
        return self._get("/clock/state")

    def tick_clock(self, base_ms: int) -> Dict[str, Any]:
        return self._post("/clock/tick", params={"base_ms": int(base_ms)})

    def seek_clock(self, time_ms: int) -> Dict[str, Any]:
        return self._post("/clock/seek", params={"time_ms": int(time_ms)})

    # -------- Replay APIs --------

    def get_replay_frame(self) -> Dict[str, Any]:
        return self._get("/replay/frame")

    def get_metadata(self) -> Dict[str, Any]:
        return self._get("/replay/metadata")
