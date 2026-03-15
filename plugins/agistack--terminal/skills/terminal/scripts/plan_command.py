#!/usr/bin/env python3
import argparse

COMMON_PLANS = [
    ("list files", "ls -la"),
    ("show current directory", "pwd"),
    ("find python files", "find . -name '*.py'"),
    ("search text", "grep -R \"keyword\" ."),
    ("show disk usage", "du -sh ."),
]

def plan_from_intent(intent: str) -> str:
    lowered = intent.lower()
    if "current directory" in lowered or "where am i" in lowered:
        return "pwd"
    if "list files" in lowered or "show files" in lowered:
        return "ls -la"
    if "python file" in lowered:
        return "find . -name '*.py'"
    if "disk usage" in lowered or "folder size" in lowered:
        return "du -sh ."
    if "search" in lowered:
        return "grep -R \"keyword\" ."
    return "# Review and edit before running\n# Example:\nls -la"

def main():
    parser = argparse.ArgumentParser(description="Plan a shell command from user intent")
    parser.add_argument("--intent", required=True, help="Natural language intent")
    args = parser.parse_args()

    command = plan_from_intent(args.intent)
    print("Suggested command:")
    print(command)

if __name__ == "__main__":
    main()
