"""
Lap Times Ingestion Script (RAW)
--------------------------------
Fetches lap-level timing data using FastF1 and writes it to S3
in JSONLines format for the RAW layer.

✔ Partition-safe for AWS Glue + Athena
✔ No duplicate columns
✔ Season / round ONLY in S3 path

Execution: Local
Target bucket: f1-replay-raw-goutham
"""

import argparse
import json
import os
from datetime import datetime, timezone

import boto3
import fastf1
import pandas as pd

# -------------------------
# Configuration
# -------------------------
RAW_BUCKET = "f1-replay-raw-goutham"
CACHE_DIR = "pipelines/ingestion/fastf1_cache"

s3 = boto3.client("s3")

# -------------------------
# Helpers
# -------------------------
def ensure_cache_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)
    fastf1.Cache.enable_cache(path)


def add_ingestion_metadata(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add metadata that is NOT part of partition keys.
    """
    df["ingestion_timestamp_utc"] = datetime.now(timezone.utc).isoformat()
    df["data_source"] = "fastf1"
    return df


def upload_jsonlines(df: pd.DataFrame, s3_key: str) -> None:
    records = json.loads(
        df.to_json(
            orient="records",
            date_format="iso",
            default_handler=str
        )
    )

    body = "\n".join(json.dumps(r) for r in records)

    s3.put_object(
        Bucket=RAW_BUCKET,
        Key=s3_key,
        Body=body.encode("utf-8"),
        ContentType="application/json"
    )

# -------------------------
# Core logic
# -------------------------
def fetch_laps(season: int, round_no: int) -> pd.DataFrame:
    print(f"🚦 Fetching lap data | season={season}, round={round_no}")

    session = fastf1.get_session(season, round_no, "R")
    session.load()

    laps = session.laps

    if laps.empty:
        raise RuntimeError("No lap data returned from FastF1")

    return laps.reset_index(drop=True)

# -------------------------
# Main
# -------------------------
def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--season", type=int, required=True)
    parser.add_argument("--round", type=int, required=True)
    args = parser.parse_args()

    ensure_cache_dir(CACHE_DIR)

    laps_df = fetch_laps(args.season, args.round)
    print(f"📦 Retrieved {len(laps_df)} laps")

    # 🔒 SAFETY: drop any duplicate columns from FastF1
    laps_df = laps_df.loc[:, ~laps_df.columns.duplicated()]

    # 🚫 CRITICAL: remove partition columns from JSON if present
    for col in ["season", "round"]:
        if col in laps_df.columns:
            laps_df.drop(columns=[col], inplace=True)

    laps_df = add_ingestion_metadata(laps_df)

    s3_key = (
        f"lap_times/"
        f"season={args.season}/"
        f"round={args.round}/"
        f"laps.jsonl"
    )

    upload_jsonlines(laps_df, s3_key)

    print(
        f"✅ Uploaded {len(laps_df)} lap records to "
        f"s3://{RAW_BUCKET}/{s3_key}"
    )


if __name__ == "__main__":
    main()
