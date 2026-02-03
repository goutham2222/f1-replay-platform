# app/services/metadata_loader.py

from app.storage.parquet_reader import (
    ParquetReader,
    S3PartitionNotFound,
)


class MetadataLoader:
    """
    Loads curated metadata from S3.
    TELEMETRY-ONLY MODE:
    - No lap windows
    - No phase resolution
    """

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
    # Drivers (USED for names + team colors)
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
            [
                "driver_number",
                "driver_code",
                "driver_name",
                "team_name",
            ]
        ]

    # --------------------------------------------------
    # Lap times (optional, KEEP for future features)
    # --------------------------------------------------
    def load_lap_times(self) -> list[dict]:
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

        required = {
            "driver_id",
            "lap_number",
            "lap_start_time_ms",
            "lap_finish_time_ms",
        }
        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"Missing lap time columns: {missing}")

        return df[
            [
                "driver_id",
                "lap_number",
                "lap_start_time_ms",
                "lap_finish_time_ms",
            ]
        ].to_dict(orient="records")

    # --------------------------------------------------
    # Track geometry
    # --------------------------------------------------
    def load_track_centerline(self):
        try:
            df = self.reader.read_partitioned_table(
                bucket=self.curated_bucket,
                dataset="track_centerline",
                season=self.season,
                round=self.round,
            )
        except S3PartitionNotFound:
            # TEMP fallback
            return self._load_placeholder_centerline()

        required = {"x", "y"}
        missing = required - set(df.columns)
        if missing:
            raise ValueError(
                f"Missing track centerline columns: {missing}"
            )

        return list(zip(df["x"].astype(float), df["y"].astype(float)))

    # --------------------------------------------------
    # Placeholder fallback
    # --------------------------------------------------
    def _load_placeholder_centerline(self):
        import math

        points = []
        radius = 1000
        for i in range(360):
            angle = math.radians(i)
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            points.append((x, y))

        return points
