import arcade
from clients.arcade.driver_status import resolve_driver_status


# --------------------------------------------------
# Placeholder driver names (client-only)
# --------------------------------------------------
DRIVER_NAME_MAP = {
    "1": "Max Verstappen",
    "11": "Sergio Perez",
    "16": "Charles Leclerc",
    "55": "Carlos Sainz",
    "44": "Lewis Hamilton",
    "63": "George Russell",
}

DEFAULT_STATUS = "Racing"


class LeaderboardRenderer:
    """
    Render-only leaderboard.
    No API calls.
    No clock access.
    No logic.
    """

    def __init__(self):
        self.entries: list[dict] = []

    def update_from_frame(self, driver_states: list[dict], time_ms: int):
        """
        Preserve ordering exactly as provided by frame.
        """
        self.entries = []

        for idx, d in enumerate(driver_states, start=1):
            driver_id = d["driver_id"]

            self.entries.append({
                "position": idx,
                "name": DRIVER_NAME_MAP.get(
                    driver_id, f"Driver {driver_id}"
                ),
                "status": resolve_driver_status(driver_id, time_ms),
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
