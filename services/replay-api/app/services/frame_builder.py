# app/services/frame_builder.py

from app.services.clock_registry import clock
from app.services.telemetry_position_builder import TelemetryPositionBuilder
from app.services.metadata_loader import MetadataLoader


class FrameBuilder:
    """
    Builds replay frames using telemetry ONLY.
    Frame order is authoritative (sorted by distance).
    """

    def __init__(self, curated_bucket: str, season: int, round: int):
        self.telemetry = TelemetryPositionBuilder(
            curated_bucket=curated_bucket,
            season=season,
            round=round,
        )

        metadata = MetadataLoader(
            curated_bucket=curated_bucket,
            season=season,
            round=round,
        )

        drivers_df = metadata.load_drivers()

        # 🔒 HARD ASSERT (fail fast, clear error)
        required = {"driver_number", "driver_code", "team_name"}
        missing = required - set(drivers_df.columns)
        if missing:
            raise RuntimeError(
                f"Driver metadata missing columns: {missing}"
            )

        # Index metadata by driver_number (dict-safe)
        self.driver_lookup = {}

        for row in drivers_df.to_dict(orient="records"):
            self.driver_lookup[int(row["driver_number"])] = {
                "driver_id": str(row["driver_number"]),
                "driver_code": row["driver_code"],
                "team": row["team_name"],
            }

    def build_frame(self) -> dict:
        if clock is None:
            raise RuntimeError("Clock not initialized")

        time_ms = clock.current_time_ms
        telemetry_states = self.telemetry.build(time_ms)

        driver_states = []

        for t in telemetry_states:
            meta = self.driver_lookup.get(t["driver_number"])
            if not meta:
                continue

            driver_states.append({
                "driver_id": meta["driver_id"],
                "driver_code": meta["driver_code"],
                "team": meta["team"],
                "x": t["x"],
                "y": t["y"],
                "distance": t["distance"],
            })

        # 🔥 AUTHORITATIVE race order
        driver_states.sort(
            key=lambda d: d["distance"],
            reverse=True,
        )

        return {
            "time_ms": time_ms,
            "phase": "TELEMETRY",
            "driver_states": driver_states,
        }
