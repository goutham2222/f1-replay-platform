import requests


class ReplayAPIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    # -------------------------
    # Clock control
    # -------------------------
    def tick(self) -> dict:
        resp = requests.post(f"{self.base_url}/clock/tick", timeout=0.5)
        resp.raise_for_status()
        return resp.json()

    def seek(self, target_time_ms: int) -> dict:
        resp = requests.post(
            f"{self.base_url}/clock/seek",
            json={"target_time_ms": target_time_ms},
            timeout=0.5,
        )
        resp.raise_for_status()
        return resp.json()

    def reset(self) -> dict:
        resp = requests.post(f"{self.base_url}/clock/reset", timeout=0.5)
        resp.raise_for_status()
        return resp.json()

    def get_clock_state(self) -> dict:
        resp = requests.get(f"{self.base_url}/clock/state", timeout=0.5)
        resp.raise_for_status()
        return resp.json()

    # -------------------------
    # Replay frame
    # -------------------------
    def get_frame(self) -> dict:
        resp = requests.get(f"{self.base_url}/replay/frame", timeout=0.5)
        resp.raise_for_status()
        return resp.json()
