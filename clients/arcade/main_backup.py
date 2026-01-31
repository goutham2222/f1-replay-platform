import arcade
import time

from clients.arcade.config import settings
from clients.arcade.replay_api_client import ReplayAPIClient
from clients.arcade.track import TrackRenderer
from clients.arcade.driver import DriverDot


class ArcadeClient(arcade.Window):
    def __init__(self):
        super().__init__(
            width=settings.WINDOW_WIDTH,
            height=settings.WINDOW_HEIGHT,
            title=settings.WINDOW_TITLE,
        )

        arcade.set_background_color(arcade.color.BLACK)

        # -----------------------------
        # Clients
        # -----------------------------
        self.replay_client = ReplayAPIClient(
            settings.REPLAY_API_BASE_URL
        )

        # -----------------------------
        # Renderers
        # -----------------------------
        self.track_renderer = TrackRenderer()
        self.drivers: dict[str, DriverDot] = {}

        # -----------------------------
        # Replay state
        # -----------------------------
        self.latest_frame: dict | None = None
        self.replay_time_ms: int = 0

    # -------------------------------------------------
    # Setup
    # -------------------------------------------------
    def setup(self):
        self.track_renderer = TrackRenderer()
        self.track_renderer.load_from_s3(
            bucket=settings.CURATED_BUCKET,
            season=settings.SEASON,
            round_=settings.ROUND,
        )

        # Schedule background frame updates (10 FPS)
        arcade.schedule(self._update_frame, 1 / 10)

    # -------------------------------------------------
    # Background update (SAFE to block briefly)
    # -------------------------------------------------
    def _update_frame(self, delta_time: float):
        self.replay_time_ms += int(delta_time * 1000)

        try:
            self.latest_frame = self.replay_client.get_frame(
                replay_time_ms=self.replay_time_ms
            )
        except Exception:
            # Never crash the render loop
            pass

    # -------------------------------------------------
    # Draw (MUST be non-blocking)
    # -------------------------------------------------
    def on_draw(self):
        arcade.start_render()

        self._draw_header()
        self.track_renderer.draw()

        if self.latest_frame:
            self._draw_drivers(self.latest_frame)

    # -------------------------------------------------
    # UI
    # -------------------------------------------------
    def _draw_header(self):
        arcade.draw_text(
            "F1 Replay Platform — Arcade Client",
            20,
            self.height - 30,
            arcade.color.WHITE,
            18,
        )

    # -------------------------------------------------
    # Drivers
    # -------------------------------------------------
    def _draw_drivers(self, frame: dict):
        for state in frame.get("driver_states", []):
            driver_id = state["driver_id"]

            if driver_id not in self.drivers:
                self.drivers[driver_id] = DriverDot()

            x = state["x"]
            y = state["y"]

            screen_x, screen_y = self.track_renderer.to_screen(x, y)
            self.drivers[driver_id].draw(screen_x, screen_y)


def main():
    window = ArcadeClient()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
