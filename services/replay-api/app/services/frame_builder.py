from app.services.clock_registry import clock
from app.services.lap_state_builder import LapStateBuilder
from app.services.metadata_loader import MetadataLoader


class FrameBuilder:
    def __init__(self, curated_bucket: str, season: int, round: int):
        self.curated_bucket = curated_bucket
        self.season = season
        self.round = round

        self.metadata = MetadataLoader(curated_bucket, season, round)
        self.lap_state_builder = LapStateBuilder(
            curated_bucket, season, round
        )

        self.race = self.metadata.load_race()
        self.drivers = self.metadata.load_drivers()

    def build_frame(self) -> dict:
        if clock is None:
            raise RuntimeError("Clock not initialized")

        time_ms = clock.current_time_ms
        driver_states = self.lap_state_builder.build_race_state(time_ms)

        return {
            "time_ms": time_ms,
            "phase": clock.phase,
            "driver_states": driver_states,
        }
