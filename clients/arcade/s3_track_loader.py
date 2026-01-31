from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from typing import List, Tuple

import boto3
import pyarrow as pa
import pyarrow.parquet as pq


class S3PartitionNotFound(Exception):
    pass


@dataclass(frozen=True)
class TrackPoint:
    x: float
    y: float


def _list_parquet_keys(bucket: str, prefix: str) -> list[str]:
    s3 = boto3.client("s3")

    keys: list[str] = []
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if key.endswith(".parquet"):
                keys.append(key)

    return keys


def _read_parquet_tables(bucket: str, keys: list[str]) -> pa.Table:
    s3 = boto3.client("s3")
    tables: list[pa.Table] = []

    for key in keys:
        body = s3.get_object(Bucket=bucket, Key=key)["Body"].read()
        table = pq.read_table(BytesIO(body))
        tables.append(table)

    if not tables:
        return pa.table({})
    return pa.concat_tables(tables, promote=True)


def load_track_from_s3(
    bucket: str,
    season: int,
    round_: int,
    dataset: str = "track_geometry",
) -> List[Tuple[float, float]]:
    """
    Returns ordered track points [(x,y), ...] from:
      s3://{bucket}/{dataset}/season={season}/round={round_}/part-*.parquet
    """
    prefix = f"{dataset}/season={season}/round={round_}/"
    keys = _list_parquet_keys(bucket=bucket, prefix=prefix)

    if not keys:
        raise S3PartitionNotFound(f"No parquet found under s3://{bucket}/{prefix}")

    table = _read_parquet_tables(bucket=bucket, keys=keys)

    if table.num_rows == 0:
        raise S3PartitionNotFound(f"Empty parquet under s3://{bucket}/{prefix}")

    # Convert to pandas only after we have the combined table
    df = table.to_pandas()

    required = {"x", "y", "point_index"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Track parquet missing columns: {sorted(missing)}")

    df = df.sort_values("point_index").reset_index(drop=True)
    return [(float(r["x"]), float(r["y"])) for _, r in df.iterrows()]
