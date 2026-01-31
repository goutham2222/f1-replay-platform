import arcade

from clients.arcade.config import settings
from clients.arcade.track import TrackRenderer
from clients.arcade.driver import DriverDot
from clients.arcade.replay_api_client import ReplayAPIClient
from clients.arcade.colors import get_team_color


class ArcadeClient(arcade.Window):
    TICK_FPS = 30
    SEEK_MS = 5_000

    def __init__(self, track_renderer: TrackRenderer):
        # Correct, version-safe way to get screen size
        screen_width, screen_height = arcade.get_display_size()

        super().__init__(
            width=screen_width,
            height=screen_height,
            title=settings.WINDOW_TITLE,
            resizable=True,
        )

        arcade.set_background_color(arcade.color.BLACK)

        self.track_renderer = track_renderer
        self.api = ReplayAPIClient(settings.REPLAY_API_BASE_URL)

        self.drivers: dict[str, DriverDot] = {}
        self.replay_time_ms: int = 0
        self.playing: bool = True

        self.track_renderer.fit_to_view(self.width, self.height)

        arcade.schedule(self._tick_replay, 1 / self.TICK_FPS)

    # ---------------------------------
    # Replay clock
    # ---------------------------------
    def _tick_replay(self, _dt: float):
        if not self.playing:
            return

        self.api.tick()
        clock = self.api.get_clock_state()
        self.replay_time_ms = clock["current_time_ms"]

    # ---------------------------------
    # Input (ESC does nothing)
    # ---------------------------------
    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.SPACE:
            self.playing = not self.playing

        elif symbol == arcade.key.LEFT:
            clock = self.api.get_clock_state()
            target = max(0, clock["current_time_ms"] - self.SEEK_MS)
            self.api.seek(target)
            self.replay_time_ms = target

        elif symbol == arcade.key.RIGHT:
            clock = self.api.get_clock_state()
            target = clock["current_time_ms"] + self.SEEK_MS
            self.api.seek(target)
            self.replay_time_ms = target

        elif symbol == arcade.key.R:
            self.api.reset()
            self.replay_time_ms = 0

    # ---------------------------------
    # Rendering
    # ---------------------------------
    def on_draw(self):
        arcade.start_render()
        self._draw_hud()
        self.track_renderer.draw()
        self._draw_drivers()
        self._draw_controls()

    def _draw_hud(self):
        arcade.draw_text(
            f"replay_time_ms: {self.replay_time_ms}",
            20,
            self.height - 40,
            arcade.color.WHITE,
            16,
        )
        arcade.draw_text(
            f"state: {'PLAYING' if self.playing else 'PAUSED'}",
            20,
            self.height - 65,
            arcade.color.YELLOW,
            14,
        )

    def _draw_controls(self):
        y = 60
        arcade.draw_text("[SPACE] Play / Pause", 20, y, arcade.color.GRAY, 12)
        arcade.draw_text("[← / →] Seek", 20, y - 18, arcade.color.GRAY, 12)
        arcade.draw_text("[R] Reset", 20, y - 36, arcade.color.GRAY, 12)

    def _draw_drivers(self):
        frame = self.api.get_frame()

        for d in frame.get("driver_states", []):
            driver_id = d["driver_id"]
            team = d.get("team", "Unknown")

            if driver_id not in self.drivers:
                self.drivers[driver_id] = DriverDot(get_team_color(team))

            sx, sy = self.track_renderer.to_screen(d["x"], d["y"])
            self.drivers[driver_id].update(sx, sy)
            self.drivers[driver_id].draw(alpha=1.0)

    def on_resize(self, width: float, height: float):
        super().on_resize(width, height)
        self.track_renderer.fit_to_view(width, height)


def main():
    track = TrackRenderer()
    track.load_from_s3(
        bucket=settings.CURATED_BUCKET,
        season=settings.SEASON,
        round_=settings.ROUND,
    )

    ArcadeClient(track)
    arcade.run()


if __name__ == "__main__":
    main()
