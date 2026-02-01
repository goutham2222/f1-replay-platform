# app/services/metadata_loader.py

from app.storage.parquet_reader import (
    ParquetReader,
    S3PartitionNotFound,
)
from app.services.phase_resolver import LapWindow


class MetadataLoader:
    def __init__(self, curated_bucket: str, season: int, round: int):
        self.curated_bucket = curated_bucket
        self.season = season
        self.round = round
        self.reader = ParquetReader()

    # --------------------------------------------------
    # Race metadata
    # --------------------------------------------------
    def load_race(self):
        try:
            df = self.reader.read_partitioned_table(
                bucket=self.curated_bucket,
                dataset="races",
                season=self.season,
            )
        except S3PartitionNotFound as e:
            raise ValueError(
                f"Race data not found for season={self.season}"
            ) from e

        race = df[df["round"] == self.round]

        if race.empty:
            raise ValueError(
                f"Race not found for season={self.season}, round={self.round}"
            )

        return race.iloc[0].to_dict()

    # --------------------------------------------------
    # Drivers
    # --------------------------------------------------
    def load_drivers(self):
        try:
            df = self.reader.read_partitioned_table(
                bucket=self.curated_bucket,
                dataset="drivers",
                season=self.season,
            )
        except S3PartitionNotFound as e:
            raise ValueError(
                f"Drivers data not found for season={self.season}"
            ) from e

        return df[
            ["driver_id", "driver_number", "driver_name", "team_name"]
        ]

    # --------------------------------------------------
    # NEW: Lap windows
    # --------------------------------------------------
    def load_lap_windows(self):
        try:
            df = self.reader.read_partitioned_table(
                bucket=self.curated_bucket,
                dataset="lap_times",
                season=self.season,
                round=self.round,
            )
        except S3PartitionNotFound as e:
            raise ValueError(
                f"Lap times not found for season={self.season}, round={self.round}"
            ) from e

        # Aggregate per lap
        grouped = (
            df.groupby("lap_number")
            .agg(
                start_ms=("lap_start_time_ms", "min"),
                finish_ms=("lap_finish_time_ms", "max"),
            )
            .reset_index()
            .sort_values("lap_number")
        )

        lap_windows = [
            LapWindow(
                lap_number=int(row.lap_number),
                start_ms=int(row.start_ms),
                finish_ms=int(row.finish_ms),
            )
            for row in grouped.itertuples(index=False)
        ]

        if not lap_windows:
            raise ValueError("No lap windows generated")

        return lap_windows
