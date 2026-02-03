import arcade
from clients.arcade.driver_status import resolve_driver_status
from clients.arcade.colors import get_team_color


class LeaderboardRenderer:
    """
    Render-only leaderboard.
    Ordering is authoritative from backend frame.
    """

    def __init__(self):
        self.entries: list[dict] = []

    def update_from_frame(self, driver_states: list[dict], time_ms: int):
        self.entries = []

        for idx, d in enumerate(driver_states, start=1):
            self.entries.append({
                "position": idx,
                "name": d.get("driver_code", d["driver_id"]),
                "status": resolve_driver_status(d["driver_id"], time_ms),
                "team": d.get("team", "Unknown"),
            })

    def draw(self, x: int, y: int):
        # Header
        arcade.draw_text(
            "POS   NAME     STATUS",
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
                f"{e['name']:<7}   "
                f"{e['status']:<8}"
            )

            color = get_team_color(e["team"])

            arcade.draw_text(
                line,
                x,
                y,
                color,
                12,
            )

            y -= 20
