#!/usr/bin/env python3
"""
github-watch setup.py
Configure token path, recipient, outputs.
Usage:
  setup.py             Interactive
  setup.py --show      Print current config
  setup.py --cleanup   Remove config
"""

import sys
import json
import os
import re

CONFIG_DIR  = os.path.expanduser("~/.openclaw/config/github-watch")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")
DATA_DIR    = os.path.expanduser("~/.openclaw/data/github-watch")

_EMAIL_RE = re.compile(r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$')
_VALID_OUTPUTS = {"email", "nextcloud"}

DEFAULTS = {
    "token_path": "~/.openclaw/secrets/github_token",
    "recipient":  "",
    "nc_path":    "/Jarvis/github-watch.md",
    "outputs":    ["email", "nextcloud"],
    "since":      "weekly",
}


def load():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, encoding="utf-8") as f:
            return json.load(f)
    return dict(DEFAULTS)


def save(cfg):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)
    print(f"Config sauvegardee: {CONFIG_PATH}")


def _validate_token_path(path):
    """Validate token path is within ~/.openclaw/."""
    expanded = os.path.expanduser(path)
    openclaw_base = os.path.expanduser("~/.openclaw")
    if not os.path.abspath(expanded).startswith(os.path.abspath(openclaw_base)):
        print(f"[WARN] Token path hors de ~/.openclaw/ : {path}")
        confirm = input("Continuer quand meme ? (y/N): ").strip().lower()
        if confirm != "y":
            return None
    return path


def _validate_email(addr):
    """Validate email address format."""
    if not addr:
        return addr
    if not _EMAIL_RE.match(addr):
        print(f"[WARN] Format email invalide: {addr}")
        return None
    return addr


def _validate_nc_path(path):
    """Validate Nextcloud path is absolute and has no traversal."""
    if not path.startswith("/"):
        print(f"[WARN] Le chemin Nextcloud doit commencer par / : {path}")
        return None
    if ".." in path:
        print(f"[WARN] Path traversal detecte: {path}")
        return None
    return path


def _validate_outputs(raw):
    """Validate output list contains only known values."""
    items = [o.strip() for o in raw.split(",") if o.strip()]
    invalid = [o for o in items if o not in _VALID_OUTPUTS]
    if invalid:
        print(f"[WARN] Outputs invalides ignores: {', '.join(invalid)}")
        items = [o for o in items if o in _VALID_OUTPUTS]
    return items


def interactive():
    cfg = load()
    print("=== GitHub Watch Setup ===\n")

    # Token path
    default_token = cfg.get("token_path", DEFAULTS["token_path"])
    val = input(f"Chemin token GitHub [{default_token}]: ").strip()
    if val:
        validated = _validate_token_path(val)
        if validated:
            cfg["token_path"] = validated
    else:
        cfg["token_path"] = default_token

    # Recipient
    default_email = cfg.get("recipient", DEFAULTS["recipient"])
    val = input(f"Email destinataire [{default_email}]: ").strip()
    if val:
        validated = _validate_email(val)
        if validated:
            cfg["recipient"] = validated
        else:
            print(f"  -> conserve la valeur actuelle: {default_email}")
    else:
        cfg["recipient"] = default_email

    # Nextcloud path
    default_nc = cfg.get("nc_path", DEFAULTS["nc_path"])
    val = input(f"Chemin Nextcloud [{default_nc}]: ").strip()
    if val:
        validated = _validate_nc_path(val)
        if validated:
            cfg["nc_path"] = validated
        else:
            print(f"  -> conserve la valeur actuelle: {default_nc}")
    else:
        cfg["nc_path"] = default_nc

    # Since
    default_since = cfg.get("since", "weekly")
    val = input(f"Periode trending (daily/weekly/monthly) [{default_since}]: ").strip()
    if val in ("daily", "weekly", "monthly"):
        cfg["since"] = val
    else:
        cfg["since"] = default_since

    # Outputs
    print(f"Outputs disponibles: {', '.join(sorted(_VALID_OUTPUTS))}")
    current = ", ".join(cfg.get("outputs", []))
    val = input(f"Outputs [{current}]: ").strip()
    if val:
        cfg["outputs"] = _validate_outputs(val)
    # else keep current

    save(cfg)
    print("\nSetup complet.")


def main():
    args = sys.argv[1:]

    if "--show" in args:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, encoding="utf-8") as f:
                print(f.read())
        else:
            print("Aucune config. Lance setup.py d'abord.")
        return

    if "--cleanup" in args:
        if os.path.exists(CONFIG_PATH):
            os.remove(CONFIG_PATH)
            print(f"Supprime: {CONFIG_PATH}")
        return

    interactive()


if __name__ == "__main__":
    main()
