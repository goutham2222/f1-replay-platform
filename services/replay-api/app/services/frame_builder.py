import pandas as pd

from app.services.metadata_loader import MetadataLoader
from app.storage.parquet_reader import (
    ParquetReader,
    S3PartitionNotFound,
)

AVERAGE_LAP_MS = 90_000  # visualization granularity only


class FrameBuilder:
    def __init__(self, curated_bucket: str, season: int, round: int):
        self.curated_bucket = curated_bucket
        self.season = season
        self.round = round

        self.reader = ParquetReader()
        self.meta = MetadataLoader(curated_bucket, season, round)

        # ----------------------------
        # Static metadata
        # ----------------------------
        self.race = self.meta.load_race()
        self.drivers = self.meta.load_drivers()

        # ----------------------------
        # Load curated lap times
        # ----------------------------
        try:
            df = self.reader.read_partitioned_table(
                bucket=self.curated_bucket,
                dataset="lap_times",
                season=self.season,
                round=self.round,
            )
        except S3PartitionNotFound as e:
            raise ValueError(
                f"Lap times not found for season={season}, round={round}"
            ) from e

        df = (
            df.dropna(subset=["lap_time_ms"])
              .sort_values(["driver_id", "lap_number"])
              .reset_index(drop=True)
        )

        if df.empty:
            raise ValueError(
                f"No lap times available for season={season}, round={round}"
            )

        # ----------------------------
        # Precompute race duration
        # ----------------------------
        total_times = (
            df.groupby("driver_id")["lap_time_ms"]
              .sum()
        )

        self.race_end_time_ms = int(total_times.max())
        self.max_lap_number = int(df["lap_number"].max())
        self.lap_times = df

    # -------------------------------------------------
    # Continuous driver state (visual only)
    # -------------------------------------------------
    def _build_driver_states(self, replay_time_ms: int) -> list[dict]:
        completed_laps = replay_time_ms // AVERAGE_LAP_MS
        current_lap = min(int(completed_laps + 1), self.max_lap_number)

        lap_progress = (replay_time_ms % AVERAGE_LAP_MS) / AVERAGE_LAP_MS

        states = []
        for _, d in self.drivers.iterrows():
            states.append({
                "driver_id": d["driver_id"],
                "driver_number": d["driver_number"],
                "driver_name": d["driver_name"],
                "team_name": d["team_name"],
                "current_lap": current_lap,
                "lap_progress": round(lap_progress, 3),
                "state": f"Completing Lap {current_lap}",
            })

        return states

    # -------------------------------------------------
    # Discrete completed laps
    # -------------------------------------------------
    def _visible_completed_laps(self, replay_time_ms: int) -> list[dict]:
        visible = self.lap_times[
            (self.lap_times["lap_number"] * AVERAGE_LAP_MS) <= replay_time_ms
        ]

        return (
            visible[["driver_id", "lap_number", "lap_time_ms"]]
            .to_dict(orient="records")
        )

    # -------------------------------------------------
    # Public frame builder (THIS WAS MISSING)
    # -------------------------------------------------
    def build_frame(self, replay_time_ms: int) -> dict:
        # -------------------------------
        # Pre-race
        # -------------------------------
        if replay_time_ms == 0:
            return {
                "race": self.race,
                "drivers": self.drivers.to_dict(orient="records"),
                "replay_time_ms": 0,
                "race_state": "Race yet to begin",
                "lap_times_count": 0,
                "visible_max_lap": 0,
                "driver_states": [],
                "laps": [],
            }

        # -------------------------------
        # Clamp replay time
        # -------------------------------
        clamped_time = min(replay_time_ms, self.race_end_time_ms)

        # -------------------------------
        # Race finished
        # -------------------------------
        if clamped_time >= self.race_end_time_ms:
            final_laps = (
                self.lap_times[["driver_id", "lap_number", "lap_time_ms"]]
                .to_dict(orient="records")
            )

            return {
                "race": self.race,
                "drivers": self.drivers.to_dict(orient="records"),
                "replay_time_ms": self.race_end_time_ms,
                "race_state": "Race Finished",
                "lap_times_count": len(final_laps),
                "visible_max_lap": self.max_lap_number,
                "driver_states": [],
                "laps": final_laps,
            }

        # -------------------------------
        # Normal race
        # -------------------------------
        laps = self._visible_completed_laps(clamped_time)
        driver_states = self._build_driver_states(clamped_time)

        visible_max_lap = max((l["lap_number"] for l in laps), default=0)

        return {
            "race": self.race,
            "drivers": self.drivers.to_dict(orient="records"),
            "replay_time_ms": clamped_time,
            "race_state": f"Completing Lap {visible_max_lap + 1}",
            "lap_times_count": len(laps),
            "visible_max_lap": visible_max_lap,
            "driver_states": driver_states,
            "laps": laps,
        }
