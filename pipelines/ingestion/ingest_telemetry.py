import fastf1
import json
import logging
import boto3
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------
# Silence FastF1 logging
# ---------------------------------
logging.getLogger("fastf1").setLevel(logging.ERROR)
logging.getLogger("fastf1.req").setLevel(logging.ERROR)

# ---------------------------------
# Config
# ---------------------------------
SEASON = 2023
ROUND = 1
SESSION = "R"

RAW_BUCKET = "f1-replay-raw-goutham"
DATASET = "telemetry_positions"

CACHE_DIR = Path(__file__).parent / "fastf1_cache"
CACHE_DIR.mkdir(exist_ok=True)

fastf1.Cache.enable_cache(str(CACHE_DIR))

s3 = boto3.client("s3")

# ---------------------------------
# Load session (POSITION DATA)
# ---------------------------------
session = fastf1.get_session(SEASON, ROUND, SESSION)
session.load()   # ✅ correct

drivers = session.drivers

# ---------------------------------
# Build JSONL records
# ---------------------------------
records = []
ingestion_ts = datetime.now(timezone.utc).isoformat()

for drv in drivers:
    pos_df = session.pos_data.get(drv)

    if pos_df is None or pos_df.empty:
        continue

    pos_df = pos_df.reset_index()

    for _, r in pos_df.iterrows():
        records.append({
            "season": SEASON,
            "round": ROUND,
            "driver_number": str(drv),
            "timestamp_ms": int(r["Time"].total_seconds() * 1000),
            "x": float(r["X"]),
            "y": float(r["Y"]),
            "z": float(r["Z"]) if "Z" in r else None,
            "ingestion_timestamp_utc": ingestion_ts,
            "data_source": "fastf1"
        })

if not records:
    raise RuntimeError("No position telemetry extracted")

payload = "\n".join(json.dumps(r) for r in records)

# ---------------------------------
# Upload to S3 (RAW)
# ---------------------------------
s3_key = (
    f"{DATASET}/"
    f"season={SEASON}/"
    f"round={ROUND}/"
    f"telemetry_positions.jsonl"
)

s3.put_object(
    Bucket=RAW_BUCKET,
    Key=s3_key,
    Body=payload.encode("utf-8"),
    ContentType="application/json"
)

print(
    f"✅ Position telemetry ingested: "
    f"s3://{RAW_BUCKET}/{s3_key} "
    f"({len(records)} records)"
)
