import arcade

from clients.arcade.replay_api_client import ReplayAPIClient
from clients.arcade.track import TrackRenderer
from clients.arcade.driver import DriverDot
from clients.arcade.colors import get_team_color
from clients.arcade.config import settings
from clients.arcade.selector import ReplaySelector
from clients.arcade.leaderboard import LeaderboardRenderer

BACKGROUND_COLOR = arcade.color.BLACK
TARGET_FPS = 60
SEEK_DELTA_MS = 5_000


class F1ReplayApp(arcade.Window):
    def __init__(self):
        super().__init__(
            settings.WINDOW_WIDTH,
            settings.WINDOW_HEIGHT,
            settings.WINDOW_TITLE,
            update_rate=1 / TARGET_FPS,
        )

        arcade.set_background_color(BACKGROUND_COLOR)

        # --------------------------------------------------
        # Selector
        # --------------------------------------------------
        self.selector = ReplaySelector()

        # --------------------------------------------------
        # API + renderers
        # --------------------------------------------------
        self.api = ReplayAPIClient(settings.REPLAY_API_BASE_URL)
        self.track_renderer = TrackRenderer()

        self.backend_ready = False
        self.backend_init_attempted = False

        self.drivers = {}
        self.leaderboard = LeaderboardRenderer()

        # --------------------------------------------------
        # Clock + playback state
        # --------------------------------------------------
        self.clock_state = None
        self.client_playing = False

        # 🔥 PLAYBACK SPEED (CLIENT-ONLY)
        # 1.0 = real time
        # 4.0 = 4x speed (recommended default)
        self.playback_speed = 4.0

        self.ui_race_time_hms = "00:00:00"
        self.last_api_error = None

    # ==========================================================
    # Update
    # ==========================================================
    def on_update(self, delta_time: float):
        if self.selector.active:
            return

        if not self.backend_ready:
            self._init_backend()
            return

        try:
            # ------------------------------
            # CLOCK STATE
            # ------------------------------
            self.clock_state = self.api.get_clock_state()

            if not self.clock_state:
                return

            self.ui_race_time_hms = self.clock_state["current_time_hms"]

            # ------------------------------
            # TICK CLOCK (SCALED)
            # ------------------------------
            if self.client_playing:
                delta_ms = int(delta_time * 1000 * self.playback_speed)

                if delta_ms > 0:
                    self.api.tick(delta_ms)
                    self.clock_state = self.api.get_clock_state()

            # ------------------------------
            # FRAME FETCH
            # ------------------------------
            frame = self.api.get_frame()
            driver_states = frame.get("driver_states", [])

            if not driver_states:
                return

            # ------------------------------
            # LEADERBOARD
            # ------------------------------
            self.leaderboard.update_from_frame(
                driver_states,
                self.clock_state["current_time_ms"],
            )

            # ------------------------------
            # DRIVERS
            # ------------------------------
            for d in driver_states:
                driver_id = d["driver_id"]
                team = d.get("team", "Unknown")
                x = d["x"]
                y = d["y"]

                if driver_id not in self.drivers:
                    self.drivers[driver_id] = DriverDot(
                        color=get_team_color(team)
                    )

                sx, sy = self.track_renderer.to_screen(x, y)

                self.drivers[driver_id].update(
                    sx,
                    sy,
                    self.clock_state["current_time_ms"],
                )

            self.last_api_error = None

        except Exception as e:
            print("[ERROR] on_update:", e)
            self.last_api_error = str(e)

    # ==========================================================
    # Backend init
    # ==========================================================
    def _init_backend(self):
        if self.backend_init_attempted:
            return

        self.backend_init_attempted = True

        try:
            self.api.reset()
            self.client_playing = False
            self.backend_ready = True
        except Exception as e:
            self.last_api_error = str(e)
            self.backend_init_attempted = False

    # ==========================================================
    # Draw
    # ==========================================================
    def on_draw(self):
        self.clear()

        if self.selector.active:
            self.selector.draw(self.width, self.height)
            return

        self.track_renderer.draw()

        render_time_ms = (
            self.clock_state["current_time_ms"]
            if self.clock_state
            else 0
        )

        for driver in self.drivers.values():
            driver.draw(render_time_ms)

        self._draw_hud()

    def _draw_hud(self):
        arcade.draw_text(
            f"time: {self.ui_race_time_hms}",
            20,
            self.height - 40,
            arcade.color.WHITE,
            18,
        )

        phase = (
            self.clock_state.get("phase", "UNKNOWN")
            if self.clock_state
            else "CONNECTING..."
        )

        arcade.draw_text(
            f"phase: {phase}",
            20,
            self.height - 70,
            arcade.color.YELLOW,
            14,
        )

        arcade.draw_text(
            f"speed: {self.playback_speed:.1f}x",
            20,
            self.height - 100,
            arcade.color.CYAN,
            14,
        )

        self.leaderboard.draw(
            x=self.width - 420,
            y=self.height - 80,
        )

        arcade.draw_text(
            "[SPACE] Play/Pause   [←/→] Seek ±5s   [ / ] Speed   [R] Reset",
            20,
            30,
            arcade.color.GRAY,
            12,
        )

    # ==========================================================
    # Input
    # ==========================================================
    def on_key_press(self, symbol: int, modifiers: int):
        if self.selector.active:
            self.selector.on_key(symbol)
            if not self.selector.active:
                self._start_selected_race()
            return

        if not self.backend_ready:
            return

        if symbol == arcade.key.SPACE:
            if self.client_playing:
                self.api.pause()
                self.client_playing = False
            else:
                self.api.play()
                self.client_playing = True

        elif symbol == arcade.key.R:
            self.api.reset()
            self.client_playing = False
            self.drivers.clear()

        elif symbol == arcade.key.RIGHT:
            self.api.seek(
                self.clock_state["current_time_ms"] + SEEK_DELTA_MS
            )
            self.drivers.clear()

        elif symbol == arcade.key.LEFT:
            self.api.seek(
                max(
                    0,
                    self.clock_state["current_time_ms"] - SEEK_DELTA_MS
                )
            )
            self.drivers.clear()

        # 🔥 SPEED CONTROLS
        elif symbol == arcade.key.BRACKETRIGHT:
            self.playback_speed = min(self.playback_speed * 2, 32.0)

        elif symbol == arcade.key.BRACKETLEFT:
            self.playback_speed = max(self.playback_speed / 2, 0.25)

    # ==========================================================
    # Selection → backend wiring
    # ==========================================================
    def _start_selected_race(self):
        # Reset frontend state
        self.backend_ready = False
        self.backend_init_attempted = False
        self.client_playing = False
        self.playback_speed = 4.0
        self.drivers.clear()
        self.clock_state = None
        self.ui_race_time_hms = "00:00:00"

        # Store selection (for future use)
        self.selected_season = self.selector.season
        self.selected_round = self.selector.round
        self.selected_session = self.selector.session

        # Reload track for selected race
        self.track_renderer = TrackRenderer()
        self.track_renderer.load_from_s3(
            settings.CURATED_BUCKET,
            self.selected_season,
            self.selected_round,
        )
        self.track_renderer.fit_to_view(self.width, self.height)

        # ✅ Recreate API client (NO extra params)
        self.api = ReplayAPIClient(settings.REPLAY_API_BASE_URL)


def main():
    app = F1ReplayApp()
    arcade.run()


if __name__ == "__main__":
    main()
