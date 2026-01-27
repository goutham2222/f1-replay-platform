"""
FastF1 Ingestion Script
----------------------
Ingests raw F1 data for a given season using the FastF1 library
and stores it in Amazon S3 (raw layer).

Execution: Local
Target Bucket: f1-replay-raw-goutham
Data Format: JSON (raw, schema-on-read)
"""

import json
import os
import logging
from datetime import datetime, timezone
from typing import Dict

import boto3
import fastf1
import pandas as pd

# -------------------------
# Suppress FastF1 logs
# -------------------------
logging.getLogger("fastf1").setLevel(logging.ERROR)
logging.getLogger("fastf1.req").setLevel(logging.ERROR)
logging.getLogger("fastf1.core").setLevel(logging.ERROR)
logging.getLogger("fastf1.api").setLevel(logging.ERROR)

# -------------------------
# Configuration
# -------------------------
RAW_BUCKET = "f1-replay-raw-goutham"
SEASON = 2023
FASTF1_CACHE_DIR = "fastf1_cache"

os.makedirs(FASTF1_CACHE_DIR, exist_ok=True)

# -------------------------
# AWS Client
# -------------------------
s3 = boto3.client("s3")

# -------------------------
# Helpers
# -------------------------
def upload_json_to_s3(payload: Dict, s3_key: str) -> None:
    body = json.dumps(payload, default=str).encode("utf-8")
    s3.put_object(
        Bucket=RAW_BUCKET,
        Key=s3_key,
        Body=body,
        ContentType="application/json"
    )


def add_ingestion_metadata(record: Dict) -> Dict:
    record["ingestion_timestamp_utc"] = datetime.now(timezone.utc).isoformat()
    record["data_source"] = "fastf1"
    return record

# -------------------------
# Ingestion Functions
# -------------------------
def ingest_races(season: int) -> None:
    try:
        schedule_df = fastf1.get_event_schedule(season)

        for _, row in schedule_df.iterrows():
            round_no = int(row["RoundNumber"])
            record = add_ingestion_metadata(row.to_dict())

            s3_key = (
                f"races/season={season}/round={round_no}/"
                f"races_{season}_{round_no}.json"
            )
            upload_json_to_s3(record, s3_key)

        print("RACES: added successfully")

    except Exception:
        print("RACES: failed")


def ingest_drivers(season: int) -> None:
    drivers = {}

    try:
        schedule_df = fastf1.get_event_schedule(season)

        for _, row in schedule_df.iterrows():
            round_no = int(row["RoundNumber"])

            if round_no <= 0:
                continue

            session = fastf1.get_session(season, round_no, "R")
            session.load()
            results_df = session.results

            for _, driver in results_df.iterrows():
                driver_id = driver.get("DriverId")

                if driver_id and driver_id not in drivers:
                    drivers[driver_id] = add_ingestion_metadata({
                        "driver_id": driver_id,
                        "driver_number": driver.get("DriverNumber"),
                        "driver_code": driver.get("Abbreviation"),
                        "driver_name": driver.get("FullName"),
                        "team_name": driver.get("TeamName")
                    })

        s3_key = f"drivers/season={season}/drivers_{season}.json"
        upload_json_to_s3(list(drivers.values()), s3_key)

        print(f"DRIVERS: added successfully ({len(drivers)} drivers)")

    except Exception:
        print("DRIVERS: failed")


def ingest_constructors(season: int) -> None:
    constructors = set()

    try:
        schedule_df = fastf1.get_event_schedule(season)

        for _, row in schedule_df.iterrows():
            round_no = int(row["RoundNumber"])

            if round_no <= 0:
                continue

            session = fastf1.get_session(season, round_no, "R")
            session.load()
            results_df = session.results

            constructors.update(results_df["TeamName"].dropna().unique())

        records = [
            add_ingestion_metadata({"constructor_name": team})
            for team in sorted(constructors)
        ]

        s3_key = f"constructors/season={season}/constructors_{season}.json"
        upload_json_to_s3(records, s3_key)

        print("CONSTRUCTORS: added successfully")

    except Exception:
        print("CONSTRUCTORS: failed")

# -------------------------
# Main
# -------------------------
def main() -> None:
    fastf1.Cache.enable_cache(FASTF1_CACHE_DIR)

    ingest_races(SEASON)
    ingest_drivers(SEASON)
    ingest_constructors(SEASON)

    print("INGESTION COMPLETED")


if __name__ == "__main__":
    main()
