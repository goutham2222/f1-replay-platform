"""
Track Geometry Ingestion Script (RAW)
------------------------------------
Extracts circuit track geometry using FastF1 position data
and writes it to S3 RAW as JSONLines.

Source: FastF1 position telemetry (single driver trace)
Execution: Local
Target bucket: f1-replay-raw-goutham
"""

import argparse
import json
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
def enable_cache():
    fastf1.Cache.enable_cache(CACHE_DIR)


def upload_jsonlines(df: pd.DataFrame, s3_key: str) -> None:
    records = df.to_dict(orient="records")
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
def fetch_track_geometry(season: int, round_no: int) -> pd.DataFrame:
    print(f"🏁 Fetching track geometry | season={season}, round={round_no}")

    session = fastf1.get_session(season, round_no, "R")
    session.load()

    pos_data = session.pos_data
    if not pos_data or not isinstance(pos_data, dict):
        raise RuntimeError("Position data not available")

    # Pick first driver deterministically
    driver_id = sorted(pos_data.keys())[0]
    driver_pos = pos_data[driver_id]

    if driver_pos.empty:
        raise RuntimeError("Selected driver has no position data")

    # Order by time to trace full lap path
    driver_pos = driver_pos.sort_values("SessionTime")

    track_df = driver_pos[["X", "Y"]].dropna().reset_index(drop=True)

    track_df["point_index"] = track_df.index
    track_df["season"] = season
    track_df["round"] = round_no
    track_df["ingestion_timestamp_utc"] = datetime.now(timezone.utc).isoformat()
    track_df["data_source"] = "fastf1"

    return track_df


# -------------------------
# Main
# -------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--season", type=int, required=True)
    parser.add_argument("--round", type=int, required=True)
    args = parser.parse_args()

    enable_cache()

    track_df = fetch_track_geometry(args.season, args.round)
    print(f"📐 Retrieved {len(track_df)} track points")

    s3_key = (
        f"tracks/"
        f"season={args.season}/"
        f"round={args.round}/"
        f"track_geometry.jsonl"
    )

    upload_jsonlines(track_df, s3_key)

    print(
        f"✅ Uploaded track geometry to "
        f"s3://{RAW_BUCKET}/{s3_key}"
    )


if __name__ == "__main__":
    main()
