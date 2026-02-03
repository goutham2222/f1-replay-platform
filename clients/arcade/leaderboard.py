import arcade
from clients.arcade.driver_status import resolve_driver_status


class LeaderboardRenderer:
    """
    Render-only leaderboard.
    Data is fully driven by backend frame.
    """

    def __init__(self):
        self.entries: list[dict] = []

    def update_from_frame(self, driver_states: list[dict], time_ms: int):
        """
        Preserve ordering exactly as provided by backend.
        """
        self.entries = []

        for idx, d in enumerate(driver_states, start=1):
            self.entries.append({
                "position": idx,
                "name": d.get("driver_code", f"Driver {d['driver_id']}"),
                "status": resolve_driver_status(d["driver_id"], time_ms),
            })

    def draw(self, x: int, y: int):
        arcade.draw_text(
            "POS   DRIVER                 STATUS",
            x,
            y,
            arcade.color.WHITE,
            14,
            bold=True,
        )

        y -= 24

        for e in self.entries:
            line = (
                f"P{e['position']:>2}   "
                f"{e['name']:<22}"
                f"{e['status']:>10}"
            )

            arcade.draw_text(
                line,
                x,
                y,
                arcade.color.LIGHT_GRAY,
                12,
            )

            y -= 20
