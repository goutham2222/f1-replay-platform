from typing import List

from app.services.telemetry_position_builder import TelemetryPositionBuilder


class LapStateBuilder:
    """
    Thin wrapper that adapts TelemetryPositionBuilder output
    into API driver_states.
    """

    def __init__(self, curated_bucket: str, season: int, round: int):
        self.telemetry = TelemetryPositionBuilder(
            curated_bucket=curated_bucket,
            season=season,
            round=round,
        )

    def build_pre_race(self, drivers: list[dict]) -> List[dict]:
        """
        Before race start, no positions yet.
        """
        return []

    def build_race_state(self, time_ms: int) -> List[dict]:
        """
        Build driver positions at replay time.
        """
        states = []

        for pos in self.telemetry.build(time_ms):
            states.append({
                "driver_id": str(pos["driver_number"]),
                "driver_number": pos["driver_number"],
                "x": pos["x"],
                "y": pos["y"],
            })

        return states
