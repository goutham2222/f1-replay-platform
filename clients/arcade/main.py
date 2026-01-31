from __future__ import annotations

import threading
import time
from typing import Optional

import arcade

from clients.arcade.config import settings
from clients.arcade.track import TrackRenderer
from clients.arcade.driver import DriverDot
from clients.arcade.colors import get_driver_color
from clients.arcade.replay_api_client import ReplayAPIClient


class FramePoller:
    """
    Background poller so the UI thread never blocks on HTTP.
    """

    def __init__(self, client: ReplayAPIClient, poll_hz: float = 10.0):
        self.client = client
        self.poll_s = max(1.0 / poll_hz, 0.05)

        self._lock = threading.Lock()
        self._latest_frame: Optional[dict] = None
        self._latest_error: Optional[str] = None

        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self):
        self._thread.start()

    def stop(self):
        self._stop.set()
        self._thread.join(timeout=1.0)

    def get_latest(self) -> tuple[Optional[dict], Optional[str]]:
        with self._lock:
            return self._latest_frame, self._latest_error

    def _run(self):
        while not self._stop.is_set():
            try:
                frame = self.client.get_frame()
                with self._lock:
                    self._latest_frame = frame
                    self._latest_error = None
            except Exception as e:
                with self._lock:
                    self._latest_error = str(e)
            time.sleep(self.poll_s)


class ArcadeClient(arcade.Window):
    def __init__(self, track_renderer: TrackRenderer):
        super().__init__(
            width=settings.WINDOW_WIDTH,
            height=settings.WINDOW_HEIGHT,
            title=settings.WINDOW_TITLE,
        )

        arcade.set_background_color(arcade.color.BLACK)

        self.track_renderer = track_renderer
        self.track_renderer.fit_to_view(self.width, self.height, padding=70)

        self.replay_client = ReplayAPIClient(settings.REPLAY_API_BASE_URL, timeout_s=0.5)
        self.poller = FramePoller(self.replay_client, poll_hz=10.0)
        self.poller.start()

        self.drivers: dict[str, DriverDot] = {}
        self.driver_order: list[str] = []  # stable color assignment

        self.last_frame: Optional[dict] = None
        self.last_error: Optional[str] = None

    def on_close(self):
        try:
            self.poller.stop()
        finally:
            super().on_close()

    def on_resize(self, width: int, height: int):
        super().on_resize(width, height)
        self.track_renderer.fit_to_view(width, height, padding=70)

    def on_update(self, delta_time: float):
        # No I/O here. Just read latest cached result.
        frame, err = self.poller.get_latest()
        if frame is not None:
            self.last_frame = frame
        self.last_error = err

    def on_draw(self):
        arcade.start_render()

        self.track_renderer.draw()
        self._draw_header()
        self._draw_drivers()

    def _draw_header(self):
        y = self.height - 30
        arcade.draw_text(
            "F1 Replay Platform — Arcade Client",
            20,
            y,
            arcade.color.WHITE,
            18,
        )

        y -= 26
        api_line = f"Replay API: {settings.REPLAY_API_BASE_URL}"
        arcade.draw_text(api_line, 20, y, arcade.color.GRAY, 12)

        y -= 22
        if self.last_error:
            arcade.draw_text(f"Replay API status: ERROR ({self.last_error})", 20, y, arcade.color.RED, 12)
        else:
            arcade.draw_text("Replay API status: OK", 20, y, arcade.color.GREEN, 12)

        if self.last_frame and "replay_time_ms" in self.last_frame:
            y -= 22
            arcade.draw_text(
                f"replay_time_ms: {self.last_frame.get('replay_time_ms')}",
                20,
                y,
                arcade.color.WHITE,
                12,
            )

    def _color_for_driver(self, driver_id: str) -> DriverDot:
        if driver_id not in self.drivers:
            if driver_id not in self.driver_order:
                self.driver_order.append(driver_id)
            idx = self.driver_order.index(driver_id)
            self.drivers[driver_id] = DriverDot(color=get_driver_color(idx))
        return self.drivers[driver_id]

    def _draw_drivers(self):
        if not self.last_frame:
            return

        states = self.last_frame.get("driver_states", [])
        if not isinstance(states, list):
            return

        for state in states:
            if not isinstance(state, dict):
                continue
            if "driver_id" not in state or "x" not in state or "y" not in state:
                continue

            driver_id = state["driver_id"]
            dot = self._color_for_driver(driver_id)

            screen_x, screen_y = self.track_renderer.to_screen(float(state["x"]), float(state["y"]))
            dot.draw(screen_x, screen_y)


def main():
    # -------------------------------
    # BLOCKING I/O: do it BEFORE UI
    # -------------------------------
    track_renderer = TrackRenderer()
    track_renderer.load_from_s3(
        bucket=settings.CURATED_BUCKET,
        season=settings.SEASON,
        round_=settings.ROUND,
    )

    # -------------------------------
    # UI starts after data ready
    # -------------------------------
    ArcadeClient(track_renderer)
    arcade.run()


if __name__ == "__main__":
    main()
