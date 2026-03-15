#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys

from weshop_client import WeShopError, query_execution


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect a WeShop execution payload by executionId.")
    parser.add_argument("--execution-id", required=True)
    args = parser.parse_args()
    try:
        payload = query_execution(args.execution_id)
    except WeShopError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1
    print(json.dumps({"ok": True, "executionId": args.execution_id, "data": payload}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
