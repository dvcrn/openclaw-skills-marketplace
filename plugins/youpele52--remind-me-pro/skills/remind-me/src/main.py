#!/usr/bin/env python3

# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

"""
Remind Me - Create, list, and cancel cron-based reminders scoped to a channel.

Usage:
    uv run main.py create <name> <message> <schedule> <channel> <to> [once]
    uv run main.py list <channel> <to>
    uv run main.py cancel id <jobId>
    uv run main.py cancel name <name>

Schedule format:
    every:<duration>   e.g. every:30m  every:1h
    cron:<expr>        e.g. cron:0 9 * * 1-5
    at:<duration>      e.g. at:20m  at:2h
"""

import sys

from service import format_cancel_output, format_create_output, format_list_output

USAGE = """\
Usage:
  remind-me create <name> <message> <schedule> <channel> <to> [once]
  remind-me list   <channel> <to>
  remind-me cancel id   <jobId>
  remind-me cancel name <name>
"""


def main():
    """Entry point — reads positional args and dispatches to the correct service function."""
    args = sys.argv[1:]

    if not args:
        print(USAGE)
        sys.exit(1)

    command = args[0].lower()

    if command == "create":
        # create <name> <message> <schedule> <channel> <to> [once]
        if len(args) < 6:
            print(
                "Usage: remind-me create <name> <message> <schedule> <channel> <to> [once]"
            )
            sys.exit(1)
        name = args[1]
        message = args[2]
        schedule = args[3]
        channel = args[4]
        to = args[5]
        once = len(args) >= 7 and args[6].lower() == "once"
        print(format_create_output(name, message, schedule, channel, to, once))

    elif command == "list":
        # list <channel> <to>
        if len(args) < 3:
            print("Usage: remind-me list <channel> <to>")
            sys.exit(1)
        channel = args[1]
        to = args[2]
        print(format_list_output(channel, to))

    elif command == "cancel":
        # cancel id <jobId>  |  cancel name <name>
        if len(args) < 3:
            print(
                "Usage: remind-me cancel id <jobId>  OR  remind-me cancel name <name>"
            )
            sys.exit(1)
        by = args[1].lower()
        value = args[2]
        if by == "id":
            print(format_cancel_output(job_id=value, name=None))
        elif by == "name":
            print(format_cancel_output(job_id=None, name=value))
        else:
            print(f"Error: Unknown cancel mode '{by}'. Use 'id' or 'name'.")
            sys.exit(1)

    else:
        print(f"Error: Unknown command '{command}'.\n")
        print(USAGE)
        sys.exit(1)


if __name__ == "__main__":
    main()
