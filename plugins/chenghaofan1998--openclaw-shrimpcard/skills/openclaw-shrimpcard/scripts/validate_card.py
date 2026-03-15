#!/usr/bin/env python3
import json
import sys

REQUIRED = [
    "schema_version",
    "card_id",
    "name",
    "tagline",
    "description",
    "top_skills",
    "owner",
    "lobster_image_desc",
]


def fail(msg):
    print("[FAIL] " + msg)
    sys.exit(1)


def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        fail(f"Cannot read JSON: {e}")


def validate(data):
    for key in REQUIRED:
        if key not in data:
            fail(f"Missing required field: {key}")

    if data.get("schema_version") != "1.0":
        fail("schema_version must be '1.0'")

    if not isinstance(data.get("top_skills"), list):
        fail("top_skills must be an array")

    if len(data.get("top_skills")) != 3:
        fail("top_skills must contain exactly 3 items")

    owner = data.get("owner")
    if not isinstance(owner, dict) or not owner.get("name"):
        fail("owner.name is required")

    desc = data.get("lobster_image_desc", "")
    if "虾" not in desc and "lobster" not in desc.lower():
        fail("lobster_image_desc must describe a lobster/shrimp image")


def main():
    if len(sys.argv) != 2:
        print("Usage: validate_card.py <json-file>")
        sys.exit(2)
    data = load_json(sys.argv[1])
    validate(data)
    print("[OK] Card JSON is valid")


if __name__ == "__main__":
    main()
