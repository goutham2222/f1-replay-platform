# app/services/telemetry_position_builder.py

from bisect import bisect_right
from typing import Dict, List

import pandas as pd

from app.storage.parquet_reader import ParquetReader


class TelemetryPositionBuilder:
    """
    Provides (x, y, distance) per driver_number for a given replay time.
    Distance = cumulative telemetry distance (meters).
    """

    def __init__(self, curated_bucket: str, season: int, round: int):
        self.reader = ParquetReader()
        self.df = self._load(curated_bucket, season, round)

        self.by_driver: Dict[int, pd.DataFrame] = {}
        self._index_and_compute_distance()

    def _load(self, bucket: str, season: int, round: int) -> pd.DataFrame:
        df = self.reader.read_partitioned_table(
            bucket=bucket,
            dataset="telemetry_positions",
            season=season,
            round=round,
        )

        required = {"driver_number", "timestamp_ms", "x", "y"}
        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"Missing telemetry columns: {missing}")

        return df

    def _index_and_compute_distance(self):
        """
        Pre-index telemetry and compute cumulative distance per driver.
        """
        for driver_number, group in self.df.groupby("driver_number"):
            group = group.sort_values("timestamp_ms").reset_index(drop=True)

            dx = group["x"].diff()
            dy = group["y"].diff()
            dist = (dx ** 2 + dy ** 2).pow(0.5).fillna(0)

            group["cum_distance"] = dist.cumsum()

            self.by_driver[int(driver_number)] = group

    def build(self, time_ms: int) -> List[dict]:
        """
        Returns list of:
        {
            driver_number,
            x,
            y,
            distance
        }
        """
        states = []

        for driver_number, df in self.by_driver.items():
            ts = df["timestamp_ms"].values
            idx = bisect_right(ts, time_ms) - 1

            if idx < 0:
                continue

            row = df.iloc[idx]

            states.append({
                "driver_number": driver_number,
                "x": float(row["x"]),
                "y": float(row["y"]),
                "distance": float(row["cum_distance"]),
            })

        return states

    