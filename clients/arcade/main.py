from __future__ import annotations

import arcade

from clients.arcade.config import load_config
from clients.arcade.replay_api import ReplayApiClient


class ArcadeApp(arcade.Window):
    """
    Minimal Arcade window for F1RP-56.

    Responsibilities:
    - Open a local Arcade window
    - Prove connectivity to Replay API (read-only)
    - Render basic status text

    Explicitly NOT responsible for:
    - Replay logic
    - Timing / animation control
    - Frame interpolation
    """

    def __init__(self, replay_client: ReplayApiClient, width: int, height: int, title: str) -> None:
        super().__init__(width=width, height=height, title=title, resizable=True)
        self._replay_client = replay_client

        # UI-only state (allowed)
        self._clock_state: dict | None = None
        self._error: str | None = None

    def setup(self) -> None:
        """
        One-time setup.
        Perform a read-only call to confirm API connectivity.
        """
        try:
            self._clock_state = self._replay_client.get_clock_state()
            self._error = None
        except Exception as exc:  # UI boundary
            self._clock_state = None
            self._error = str(exc)

    def on_draw(self) -> None:
        arcade.start_render()

        x = 20
        y = self.height - 30
        line = 22

        arcade.draw_text(
            "F1 Replay Platform — Arcade Client",
            x, y,
            arcade.color.WHITE,
            font_size=18,
        )

        y -= line * 2
        arcade.draw_text(
            f"Replay API: {self._replay_client.base_url}",
            x,
            y,
            arcade.color.LIGHT_GRAY,
            font_size=14,
        )

        y -= line * 2

        if self._error:
            arcade.draw_text(
                "Replay API status: ERROR",
                x,
                y,
                arcade.color.RED,
                font_size=14,
            )
            y -= line
            arcade.draw_text(
                self._error,
                x,
                y,
                arcade.color.RED,
                font_size=12,
                width=self.width - 40,
                multiline=True,
            )
            return

        arcade.draw_text(
            "Replay API status: OK",
            x,
            y,
            arcade.color.GREEN,
            font_size=14,
        )

        y -= line

        if isinstance(self._clock_state, dict):
            arcade.draw_text(
                f"/clock/state keys: {', '.join(sorted(self._clock_state.keys()))}",
                x,
                y,
                arcade.color.LIGHT_GRAY,
                font_size=12,
                width=self.width - 40,
                multiline=True,
            )

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        """
        Temporary utility:
        - Press 'R' to re-fetch /clock/state
        """
        if symbol == arcade.key.R:
            try:
                self._clock_state = self._replay_client.get_clock_state()
                self._error = None
            except Exception as exc:
                self._clock_state = None
                self._error = str(exc)


def main() -> None:
    cfg = load_config()

    replay_client = ReplayApiClient(
        base_url=cfg.replay_api_base_url,
    )

    window = ArcadeApp(
        replay_client=replay_client,
        width=cfg.window_width,
        height=cfg.window_height,
        title=cfg.window_title,
    )
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
