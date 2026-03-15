#!/usr/bin/env python3

HIGH_RISK_TOKENS = [
    " rm ", "rm -", " mv ", "chmod ", "chown ",
    " kill ", "pkill ", "killall ",
    " apt ", "yum ", "brew uninstall", "pip uninstall",
    "> ", ">> ", "sed -i", "find . -delete"
]

def normalize(cmd: str) -> str:
    return f" {cmd.strip()} "

def risk_level(command: str) -> str:
    cmd = normalize(command)
    for token in HIGH_RISK_TOKENS:
        if token in cmd:
            return "high"
    return "normal"

def requires_confirmation(command: str) -> bool:
    return risk_level(command) == "high"
