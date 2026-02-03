from app.services.clock_registry import clock
from app.services.telemetry_position_builder import TelemetryPositionBuilder
from app.services.metadata_loader import MetadataLoader


class FrameBuilder:
    """
    Builds replay frames using telemetry positions ONLY,
    enriched with driver metadata.
    """

    def __init__(self, curated_bucket: str, season: int, round: int):
        # Telemetry (x, y over time)
        self.telemetry = TelemetryPositionBuilder(
            curated_bucket=curated_bucket,
            season=season,
            round=round,
        )

        # Driver metadata (name, team, number)
        metadata = MetadataLoader(
            curated_bucket=curated_bucket,
            season=season,
            round=round,
        )

        drivers_df = metadata.load_drivers()

        # Index by driver_number for fast lookup
        self.driver_lookup = {
            int(row["driver_number"]): {
                "driver_id": str(row["driver_number"]),
                "driver_name": row["driver_name"],
                "team": row["team_name"],
            }
            for _, row in drivers_df.iterrows()
        }

    def build_frame(self) -> dict:
        if clock is None:
            raise RuntimeError("Clock not initialized")

        time_ms = clock.current_time_ms

        telemetry_states = self.telemetry.build(time_ms)

        driver_states = []

        for t in telemetry_states:
            driver_number = int(t["driver_number"])

            meta = self.driver_lookup.get(driver_number)
            if not meta:
                # Skip if metadata missing (should not happen)
                continue

            driver_states.append({
                "driver_id": meta["driver_id"],
                "driver_name": meta["driver_name"],
                "team": meta["team"],
                "x": t["x"],
                "y": t["y"],
            })

        return {
            "time_ms": time_ms,
            "phase": "TELEMETRY",
            "driver_states": driver_states,
        }
