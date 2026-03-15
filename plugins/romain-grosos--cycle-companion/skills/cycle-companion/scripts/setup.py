#!/usr/bin/env python3
"""
cycle-companion setup - Configure cycle parameters.
Usage:
  setup.py                   Interactive setup
  setup.py --update-date YYYY-MM-DD   Update last period date only
  setup.py --show            Show current config
  setup.py --cleanup         Remove config file
"""

import sys
import json
import os
from datetime import date

CONFIG_DIR = os.path.expanduser("~/.openclaw/config/cycle-companion")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")

DEFAULTS = {
    "last_period_date": None,
    "cycle_length": 28,
    "luteal_length": 14,
    "pms_days": 7,
    "menstruation_days": 5,
    "language": "fr",
    "notification_time": "08:00",
    "outputs": [],
}


def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, encoding="utf-8") as f:
            cfg = json.load(f)
        # Merge with defaults for new fields
        for k, v in DEFAULTS.items():
            cfg.setdefault(k, v)
        return cfg
    return dict(DEFAULTS)


def save_config(cfg):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)
    print(f"Config saved to {CONFIG_PATH}")


def parse_date(s):
    try:
        d = date.fromisoformat(s)
        if d > date.today():
            print("  [WARN] Date is in the future.")
            return None
        return s
    except ValueError:
        return None


def validate_cross_params(cfg):
    """Validate cross-parameter consistency. Returns list of error strings."""
    errors = []
    cycle_length = cfg.get("cycle_length", 28)
    luteal_length = cfg.get("luteal_length", 14)
    pms_days = cfg.get("pms_days", 7)
    menstruation_days = cfg.get("menstruation_days", 5)

    if luteal_length >= cycle_length:
        errors.append(f"luteal_length ({luteal_length}) must be < cycle_length ({cycle_length})")

    ovulation_start = cycle_length - luteal_length - 2
    if ovulation_start <= menstruation_days:
        errors.append(
            f"Phase overlap: ovulation at day {ovulation_start}, "
            f"menstruation lasts {menstruation_days} days"
        )

    luteal_start = cycle_length - luteal_length + 1
    pms_start = cycle_length - pms_days
    if pms_days > 0 and pms_start < luteal_start:
        errors.append(
            f"pms_days ({pms_days}) too large for luteal phase "
            f"(luteal starts day {luteal_start})"
        )

    return errors


def _input_int(prompt, current, min_val, max_val):
    """Prompt for an integer in range, return current if empty/invalid."""
    val = input(f"{prompt} [{current}]: ").strip()
    if not val:
        return current
    if val.isdigit() and min_val <= int(val) <= max_val:
        return int(val)
    print(f"  Valeur ignorée (attendu: {min_val}-{max_val})")
    return current


def interactive_setup():
    cfg = load_config()

    print("=== Cycle Companion Setup ===")
    print()

    # Last period date
    while True:
        default = cfg.get("last_period_date") or date.today().isoformat()
        val = input(f"Date des dernières règles / Last period date (YYYY-MM-DD) [{default}]: ").strip()
        if not val:
            val = default
        if parse_date(val):
            cfg["last_period_date"] = val
            break
        print("Format invalide. Exemple: 2026-02-15")

    # Cycle length
    cfg["cycle_length"] = _input_int(
        "Durée du cycle (jours) / Cycle length (18-45)",
        cfg.get("cycle_length", 28), 18, 45
    )

    # Luteal length
    cfg["luteal_length"] = _input_int(
        "Durée phase lutéale / Luteal phase length (10-16)",
        cfg.get("luteal_length", 14), 10, 16
    )

    # Menstruation days
    cfg["menstruation_days"] = _input_int(
        "Durée des règles (jours) / Menstruation days (2-8)",
        cfg.get("menstruation_days", 5), 2, 8
    )

    # PMS days
    cfg["pms_days"] = _input_int(
        "Jours de SPM / PMS days (0-14, 0=désactivé)",
        cfg.get("pms_days", 7), 0, 14
    )

    # Cross-validate
    errors = validate_cross_params(cfg)
    if errors:
        print()
        print("ERREURS de cohérence :")
        for e in errors:
            print(f"  - {e}")
        print("Corrigez les valeurs et relancez setup.py.")
        sys.exit(1)

    # Language
    default = cfg.get("language", "fr")
    val = input(f"Langue / Language (fr/en) [{default}]: ").strip().lower()
    if val in ("fr", "en"):
        cfg["language"] = val

    # Notification time
    default_time = cfg.get("notification_time", "08:00")
    val = input(f"Heure de notification / Notification time (HH:MM) [{default_time}]: ").strip()
    if val:
        parts = val.split(":")
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            h, m = int(parts[0]), int(parts[1])
            if 0 <= h <= 23 and 0 <= m <= 59:
                cfg["notification_time"] = f"{h:02d}:{m:02d}"
            else:
                print("  Heure ignorée (attendu: 00:00 - 23:59)")
        else:
            print("  Heure ignorée (format: HH:MM)")

    # Outputs
    print()
    print("Outputs disponibles: telegram, file")
    print("(laisser vide pour configurer plus tard / leave empty to configure later)")
    current = ", ".join(cfg.get("outputs", []))
    val = input(f"Outputs [{current or 'none'}]: ").strip()
    if val:
        valid_outputs = {"telegram", "file"}
        outputs = [o.strip() for o in val.split(",") if o.strip() in valid_outputs]
        if outputs:
            cfg["outputs"] = outputs
        else:
            print("  Aucun output valide reconnu")

    # Telegram chat_id (if telegram output)
    if "telegram" in cfg.get("outputs", []):
        default_id = cfg.get("telegram_chat_id", "")
        val = input(f"Telegram chat_id [{default_id}]: ").strip()
        if val:
            cfg["telegram_chat_id"] = val

    # File output path (if file output)
    if "file" in cfg.get("outputs", []):
        default_path = cfg.get("file_output_path", "~/.openclaw/data/cycle-companion/log.txt")
        val = input(f"File output path [{default_path}]: ").strip()
        cfg["file_output_path"] = val or default_path

    save_config(cfg)
    print()
    print("Setup complet. Lance: python3 cycle.py status")


def main():
    args = sys.argv[1:]

    if "--show" in args:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, encoding="utf-8") as f:
                print(f.read())
        else:
            print("No config found. Run setup.py first.")
        return

    if "--cleanup" in args:
        if os.path.exists(CONFIG_PATH):
            os.remove(CONFIG_PATH)
            print(f"Removed {CONFIG_PATH}")
        else:
            print("Nothing to remove.")
        return

    if "--update-date" in args:
        idx = args.index("--update-date")
        if idx + 1 >= len(args):
            print("Usage: setup.py --update-date YYYY-MM-DD")
            sys.exit(1)
        new_date = args[idx + 1]
        if not parse_date(new_date):
            print(f"Invalid date: {new_date}")
            sys.exit(1)
        cfg = load_config()
        cfg["last_period_date"] = new_date
        save_config(cfg)
        print(f"Last period date updated to {new_date}")
        return

    interactive_setup()


if __name__ == "__main__":
    main()
