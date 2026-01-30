import pandas as pd

from app.services.metadata_loader import MetadataLoader
from app.storage.parquet_reader import (
    ParquetReader,
    S3PartitionNotFound,
)


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
        # Load track geometry
        # ----------------------------
        try:
            track_df = self.reader.read_partitioned_table(
                bucket=self.curated_bucket,
                dataset="track_geometry",
                season=self.season,
                round=self.round,
            )
        except S3PartitionNotFound as e:
            raise ValueError(
                f"Track geometry not found for season={season}, round={round}"
            ) from e

        track_df = (
            track_df
            .sort_values("point_index")
            .reset_index(drop=True)
        )

        if track_df.empty:
            raise ValueError("Empty track geometry")

        self.track_points = track_df[["x", "y"]]
        self.track_len = len(self.track_points)

        # ----------------------------
        # Load lap times
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
            raise ValueError("No lap times available")

        self.lap_times = df
        self.max_lap_number = int(df["lap_number"].max())

        # Total race duration = slowest driver total
        self.race_end_time_ms = int(
            df.groupby("driver_id")["lap_time_ms"].sum().max()
        )

    # -------------------------------------------------
    # Per-driver state (CORRECT MODEL)
    # -------------------------------------------------
    def _build_driver_states(self, replay_time_ms: int) -> list[dict]:
        states = []

        for _, d in self.drivers.iterrows():
            driver_id = d["driver_id"]

            driver_laps = self.lap_times[
                self.lap_times["driver_id"] == driver_id
            ]

            elapsed = replay_time_ms
            completed_laps = 0

            for _, lap in driver_laps.iterrows():
                if elapsed >= lap["lap_time_ms"]:
                    elapsed -= lap["lap_time_ms"]
                    completed_laps += 1
                else:
                    break

            current_lap = min(completed_laps + 1, self.max_lap_number)

            if completed_laps < len(driver_laps):
                lap_duration = driver_laps.iloc[completed_laps]["lap_time_ms"]
                lap_progress = elapsed / lap_duration
            else:
                lap_progress = 1.0

            lap_progress = max(0.0, min(1.0, lap_progress))

            point_idx = int(lap_progress * (self.track_len - 1))
            point_idx = max(0, min(self.track_len - 1, point_idx))

            x = float(self.track_points.iloc[point_idx]["x"])
            y = float(self.track_points.iloc[point_idx]["y"])

            states.append({
                "driver_id": driver_id,
                "driver_number": d["driver_number"],
                "driver_name": d["driver_name"],
                "team_name": d["team_name"],
                "current_lap": current_lap,
                "lap_progress": round(lap_progress, 3),
                "x": x,
                "y": y,
                "state": f"Completing Lap {current_lap}",
            })

        return states

    # -------------------------------------------------
    # Public frame builder
    # -------------------------------------------------
    def build_frame(self, replay_time_ms: int) -> dict:
        clamped_time = min(replay_time_ms, self.race_end_time_ms)

        if clamped_time == 0:
            return {
                "race": self.race,
                "drivers": self.drivers.to_dict(orient="records"),
                "replay_time_ms": 0,
                "race_state": "Race yet to begin",
                "driver_states": [],
            }

        driver_states = self._build_driver_states(clamped_time)

        return {
            "race": self.race,
            "drivers": self.drivers.to_dict(orient="records"),
            "replay_time_ms": clamped_time,
            "race_state": "Race Running",
            "driver_states": driver_states,
        }
