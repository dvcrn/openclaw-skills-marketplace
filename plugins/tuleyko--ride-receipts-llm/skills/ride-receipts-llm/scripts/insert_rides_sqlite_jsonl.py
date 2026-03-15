#!/usr/bin/env python3
"""Insert extracted rides JSONL into SQLite.

Input: JSONL (one ride per line) following the ride-receipts-llm schema.
Idempotent due to UNIQUE(provider, gmail_message_id) ON CONFLICT REPLACE.
"""

import argparse
import json
import sqlite3
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--schema", required=True)
    ap.add_argument("--rides-jsonl", required=True)
    args = ap.parse_args()

    db_path = Path(args.db)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript(Path(args.schema).read_text(encoding="utf-8"))

    n = 0

    with open(args.rides_jsonl, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)

            provider = obj.get("provider")
            src = obj.get("source") or {}
            ride = obj.get("ride") or {}

            gmail_message_id = src.get("gmail_message_id")
            if not provider or not gmail_message_id:
                continue

            extracted_ride_json = json.dumps(obj, ensure_ascii=False)
            source_email_json = json.dumps(src, ensure_ascii=False)

            conn.execute(
                """
                INSERT INTO rides(
                  provider, gmail_message_id, email_date_text, subject,
                  start_time_text, end_time_text,
                  total_text, currency, amount,
                  pickup, dropoff, pickup_city, pickup_country, dropoff_city, dropoff_country,
                  payment_method, driver, distance_text, duration_text,
                  notes,
                  source_email_json, extracted_ride_json
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    provider,
                    gmail_message_id,
                    src.get("email_date"),
                    src.get("subject"),
                    ride.get("start_time_text"),
                    ride.get("end_time_text"),
                    ride.get("total_text"),
                    ride.get("currency"),
                    ride.get("amount"),
                    ride.get("pickup"),
                    ride.get("dropoff"),
                    ride.get("pickup_city"),
                    ride.get("pickup_country"),
                    ride.get("dropoff_city"),
                    ride.get("dropoff_country"),
                    ride.get("payment_method"),
                    ride.get("driver"),
                    ride.get("distance_text"),
                    ride.get("duration_text"),
                    ride.get("notes"),
                    source_email_json,
                    extracted_ride_json,
                ),
            )
            n += 1

    conn.commit()
    conn.close()

    print(f"Inserted {n} rides into {db_path}")


if __name__ == "__main__":
    main()
