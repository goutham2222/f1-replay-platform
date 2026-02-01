from bisect import bisect_right
from typing import Dict, List

import pandas as pd

from app.storage.parquet_reader import ParquetReader


class TelemetryPositionBuilder:
    """
    Provides (x, y) position per driver_number for a given replay time.
    Uses last-known position <= time_ms (step interpolation).
    """

    def __init__(self, curated_bucket: str, season: int, round: int):
        self.reader = ParquetReader()
        self.df = self._load(curated_bucket, season, round)

        # Pre-index telemetry by driver_number
        self.by_driver: Dict[int, pd.DataFrame] = {}

        for driver_number, group in self.df.groupby("driver_number"):
            group = group.sort_values("timestamp_ms")
            self.by_driver[int(driver_number)] = group.reset_index(drop=True)

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

    def build(self, time_ms: int) -> List[dict]:
        """
        Returns list of:
        {
          driver_number,
          x,
          y
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
            })

        return states
