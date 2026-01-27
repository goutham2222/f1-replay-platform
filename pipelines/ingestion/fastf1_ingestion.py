"""
FastF1 Ingestion Script
----------------------
Ingests raw F1 data for a given season using the FastF1 library
and stores it in Amazon S3 (raw layer).

Execution: Local
Target Bucket: f1-replay-raw-goutham
Data Format: JSONLines (newline-delimited JSON)
"""

import json
import os
from datetime import datetime, timezone
from typing import List, Dict

import boto3
import fastf1
import pandas as pd

# -------------------------
# Configuration
# -------------------------
RAW_BUCKET = "f1-replay-raw-goutham"
SEASON = 2023
FASTF1_CACHE_DIR = "fastf1_cache"

# -------------------------
# AWS Client
# -------------------------
s3 = boto3.client("s3")


# -------------------------
# Helpers
# -------------------------
def add_ingestion_metadata(record: Dict) -> Dict:
    record["ingestion_timestamp_utc"] = datetime.now(timezone.utc).isoformat()
    record["data_source"] = "fastf1"
    return record


def upload_jsonlines_to_s3(records: List[Dict], s3_key: str) -> None:
    """
    Upload records as newline-delimited JSON (JSONLines).
    """
    body = "\n".join(json.dumps(r, default=str) for r in records)

    s3.put_object(
        Bucket=RAW_BUCKET,
        Key=s3_key,
        Body=body.encode("utf-8"),
        ContentType="application/json"
    )


# -------------------------
# Ingestion Functions
# -------------------------
def ingest_races(season: int) -> None:
    """
    Ingest race-level metadata.
    One dataset (table) per season.
    """
    schedule_df = fastf1.get_event_schedule(season)

    records = []
    for _, row in schedule_df.iterrows():
        record = add_ingestion_metadata(row.to_dict())
        records.append(record)

    s3_key = f"races/season={season}/races_{season}.jsonl"
    upload_jsonlines_to_s3(records, s3_key)

    print(f"[RACES] Season {season}: {len(records)} records written")


def ingest_drivers(season: int) -> None:
    """
    Ingest unique drivers for the season.
    """
    drivers = {}

    schedule_df = fastf1.get_event_schedule(season)

    for _, row in schedule_df.iterrows():
        round_no = int(row["RoundNumber"])

        try:
            session = fastf1.get_session(season, round_no, "R")
            session.load()

            results_df = session.results

            for _, driver in results_df.iterrows():
                driver_id = driver.get("DriverId")
                if not driver_id or driver_id in drivers:
                    continue

                drivers[driver_id] = add_ingestion_metadata({
                    "driver_id": driver_id,
                    "driver_number": driver.get("DriverNumber"),
                    "driver_code": driver.get("Abbreviation"),
                    "driver_name": driver.get("FullName"),
                    "team_name": driver.get("TeamName")
                })

        except Exception:
            continue

    records = list(drivers.values())

    s3_key = f"drivers/season={season}/drivers_{season}.jsonl"
    upload_jsonlines_to_s3(records, s3_key)

    print(f"[DRIVERS] Season {season}: {len(records)} records written")


def ingest_constructors(season: int) -> None:
    """
    Ingest constructors (teams).
    """
    constructors = set()

    schedule_df = fastf1.get_event_schedule(season)

    for _, row in schedule_df.iterrows():
        round_no = int(row["RoundNumber"])

        try:
            session = fastf1.get_session(season, round_no, "R")
            session.load()
            constructors.update(session.results["TeamName"].dropna().unique())
        except Exception:
            continue

    records = [
        add_ingestion_metadata({"constructor_name": team})
        for team in sorted(constructors)
    ]

    s3_key = f"constructors/season={season}/constructors_{season}.jsonl"
    upload_jsonlines_to_s3(records, s3_key)

    print(f"[CONSTRUCTORS] Season {season}: {len(records)} records written")


# -------------------------
# Main
# -------------------------
def main() -> None:
    os.makedirs(FASTF1_CACHE_DIR, exist_ok=True)
    fastf1.Cache.enable_cache(FASTF1_CACHE_DIR)

    print("Starting FastF1 ingestion")
    print(f"Season: {SEASON}")
    print(f"Target bucket: {RAW_BUCKET}")

    ingest_races(SEASON)
    ingest_drivers(SEASON)
    ingest_constructors(SEASON)

    print("FastF1 ingestion completed successfully")


if __name__ == "__main__":
    main()
