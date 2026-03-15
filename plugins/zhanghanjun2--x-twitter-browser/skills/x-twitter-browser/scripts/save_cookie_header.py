#!/usr/bin/env python3
from __future__ import annotations

import argparse

from session_lib import (
    load_cookie_header,
    save_cookie_to_config,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Save an X cookie header to ~/.x-twitter-browser/config.json")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--cookie-header", help="Raw Cookie header string")
    source.add_argument("--cookie-file", help="File containing the raw Cookie header string")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cookie_header = load_cookie_header(args.cookie_header, args.cookie_file)
    config_path = save_cookie_to_config(cookie_header)
    print(f"Saved cookie to {config_path}")


if __name__ == "__main__":
    main()
