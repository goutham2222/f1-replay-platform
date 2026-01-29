from app.storage.parquet_reader import (
    ParquetReader,
    S3PartitionNotFound,
)


class MetadataLoader:
    def __init__(self, curated_bucket: str, season: int, round: int):
        self.curated_bucket = curated_bucket
        self.season = season
        self.round = round
        self.reader = ParquetReader()

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
