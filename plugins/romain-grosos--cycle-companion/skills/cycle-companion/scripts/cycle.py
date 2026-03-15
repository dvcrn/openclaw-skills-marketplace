#!/usr/bin/env python3
"""
cycle-companion - Menstrual cycle tracker for partners.
Usage:
  cycle.py status            Print current phase info (JSON)
  cycle.py next-transition   Print next phase change date + phase (JSON)
  cycle.py schedule-cron     Output cron job payload for next transition notification
  cycle.py delete-cron       Output cron deletion payloads for all cycle-companion jobs
  cycle.py --date YYYY-MM-DD status   Simulate status for a given date (dry-run)
"""

import sys
import json
import os
from datetime import date, timedelta

CONFIG_PATH = os.path.expanduser("~/.openclaw/config/cycle-companion/config.json")

# ---------------------------------------------------------------------------
# Phase data (bilingual) — includes fertility info
# ---------------------------------------------------------------------------

PHASES = {
    "fr": {
        "menstruation": {
            "name": "Menstruation",
            "description": "Chute hormonale, élimination de l'endomètre. Fatigue, crampes possibles, repli sur soi.",
            "energy": "Basse",
            "mood": "Fatigue, sensibilité, besoin de calme",
            "fertility": "Très faible (mais non nulle en cas de cycle court)",
            "tips": [
                "Être présent sans imposer de conversation",
                "Chaleur (bouillotte), chocolat noir, boissons chaudes",
                "Éviter les sorties ou projets exigeants",
                "Valider les inconforts sans minimiser",
            ],
            "avoid": ["Discussions importantes ou conflictuelles", "Pression sociale ou logistique"],
        },
        "follicular": {
            "name": "Phase folliculaire",
            "description": "Montée des œstrogènes. Énergie croissante, sociabilité, créativité en hausse.",
            "energy": "Croissante",
            "mood": "Bonne humeur, ouverture, confiance en hausse",
            "fertility": "Croissante — les spermatozoïdes peuvent survivre jusqu'à 5 jours",
            "tips": [
                "Proposer des sorties et activités nouvelles",
                "Bon moment pour aborder les sujets importants",
                "Projets communs, plans futurs",
                "Libido en hausse en fin de phase",
            ],
            "avoid": [],
        },
        "ovulation": {
            "name": "Ovulation",
            "description": "Pic de LH, libération de l'ovocyte. Énergie et libido maximales.",
            "energy": "Maximale",
            "mood": "Extravertie, confiante, rayonnante",
            "fertility": "MAXIMALE — fenêtre de fertilité la plus haute (ovocyte viable 12-24h)",
            "tips": [
                "Moments de complicité et d'intimité",
                "Sorties, restaurants, événements sociaux",
                "Conversations profondes bien reçues",
            ],
            "avoid": [],
        },
        "luteal": {
            "name": "Phase lutéale",
            "description": "Progestérone en hausse puis chute progressive. Besoin de sécurité émotionnelle.",
            "energy": "Décroissante",
            "mood": "Intérieure, sensible, besoin de stabilité",
            "fertility": "Faible à nulle — l'ovocyte n'est plus viable",
            "tips": [
                "Être stable et prévisible, pas de surprises",
                "Valider les émotions sans argumenter",
                "Activités calmes : films, repas maison",
                "Ne pas prendre les sautes d'humeur personnellement",
            ],
            "avoid": ["Discussions conflictuelles ou critiques", "Changements de plans de dernière minute"],
        },
        "pms": {
            "name": "SPM",
            "description": "Chute hormonale imminente. Irritabilité, hypersensibilité, ballonnements, fatigue.",
            "energy": "Très basse",
            "mood": "Irritabilité, hypersensibilité, besoin fort de calme",
            "fertility": "Nulle — phase infertile",
            "tips": [
                "Patience maximale",
                "Anticiper les besoins sans attendre qu'elle demande",
                "Repas préférés, environnement calme",
                "Validation émotionnelle, pas de rationalisation",
            ],
            "avoid": ["Toute discussion importante", "Critiques même légères", "Décisions importantes"],
        },
    },
    "en": {
        "menstruation": {
            "name": "Menstruation",
            "description": "Hormonal drop, shedding of uterine lining. Fatigue, possible cramps, introverted.",
            "energy": "Low",
            "mood": "Tired, sensitive, introverted",
            "fertility": "Very low (but not zero with short cycles)",
            "tips": [
                "Be present without pushing conversation",
                "Warmth (heating pad), dark chocolate, warm drinks",
                "Avoid demanding outings or projects",
                "Acknowledge discomfort without minimizing it",
            ],
            "avoid": ["Important or conflictual discussions", "Social or logistical pressure"],
        },
        "follicular": {
            "name": "Follicular phase",
            "description": "Rising estrogen, follicle maturation. Growing energy, sociability, creativity.",
            "energy": "Rising",
            "mood": "Good mood, openness, growing confidence",
            "fertility": "Rising — sperm can survive up to 5 days",
            "tips": [
                "Suggest outings and new activities",
                "Good time to bring up important topics",
                "Joint projects and future plans",
                "Libido rising toward end of phase",
            ],
            "avoid": [],
        },
        "ovulation": {
            "name": "Ovulation",
            "description": "LH surge, egg release. Peak energy and libido, easy communication.",
            "energy": "Peak",
            "mood": "Extroverted, confident, radiant",
            "fertility": "PEAK — highest fertility window (egg viable 12-24h)",
            "tips": [
                "Quality time and intimacy",
                "Dates, restaurants, social events",
                "Deep conversations are well received",
            ],
            "avoid": [],
        },
        "luteal": {
            "name": "Luteal phase",
            "description": "Progesterone rises then drops. Need for emotional security.",
            "energy": "Decreasing",
            "mood": "Introspective, sensitive, needs stability",
            "fertility": "Low to none — egg is no longer viable",
            "tips": [
                "Be stable and predictable (no surprises)",
                "Validate emotions without arguing",
                "Calm activities: movies, home-cooked meals",
                "Do not take mood swings personally",
            ],
            "avoid": ["Conflictual or critical discussions", "Last-minute plan changes"],
        },
        "pms": {
            "name": "PMS",
            "description": "Imminent hormonal crash. Irritability, hypersensitivity, bloating, fatigue.",
            "energy": "Very low",
            "mood": "Irritable, hypersensitive, strong need for calm",
            "fertility": "None — infertile phase",
            "tips": [
                "Maximum patience",
                "Anticipate needs before she has to ask",
                "Favorite meals, calm environment",
                "Emotional validation, not rationalization",
            ],
            "avoid": ["Any important discussion", "Even mild criticism", "Planning or decisions"],
        },
    },
}


# ---------------------------------------------------------------------------
# Config loading + validation
# ---------------------------------------------------------------------------

def load_config():
    if not os.path.exists(CONFIG_PATH):
        print(json.dumps({"error": f"Config not found at {CONFIG_PATH}. Run setup.py first."}))
        sys.exit(1)
    with open(CONFIG_PATH, encoding="utf-8") as f:
        cfg = json.load(f)
    validate_config(cfg)
    return cfg


def validate_config(cfg):
    """Validate cross-parameter consistency. Exits on fatal errors, warns on issues."""
    cycle_length = cfg.get("cycle_length", 28)
    luteal_length = cfg.get("luteal_length", 14)
    pms_days = cfg.get("pms_days", 7)
    menstruation_days = cfg.get("menstruation_days", 5)

    errors = []

    if cycle_length < 18 or cycle_length > 45:
        errors.append(f"cycle_length={cycle_length} out of range (18-45)")

    if luteal_length < 10 or luteal_length > 16:
        errors.append(f"luteal_length={luteal_length} out of range (10-16)")

    if luteal_length >= cycle_length:
        errors.append(f"luteal_length ({luteal_length}) must be < cycle_length ({cycle_length})")

    if menstruation_days < 2 or menstruation_days > 8:
        errors.append(f"menstruation_days={menstruation_days} out of range (2-8)")

    if pms_days < 0 or pms_days > 14:
        errors.append(f"pms_days={pms_days} out of range (0-14)")

    # Check that phases don't overlap: menstruation + follicular must fit before ovulation
    ovulation_start = cycle_length - luteal_length - 2
    if ovulation_start <= menstruation_days:
        errors.append(
            f"Phase overlap: ovulation starts at day {ovulation_start} "
            f"but menstruation lasts {menstruation_days} days. "
            f"Increase cycle_length or decrease luteal_length."
        )

    # Check PMS doesn't eat into luteal completely
    luteal_start = cycle_length - luteal_length + 1
    pms_start = cycle_length - pms_days
    if pms_days > 0 and pms_start < luteal_start:
        errors.append(
            f"pms_days ({pms_days}) exceeds luteal phase length "
            f"(luteal starts day {luteal_start}, pms starts day {pms_start}). "
            f"Decrease pms_days or luteal_length."
        )

    if errors:
        print(json.dumps({"error": "Invalid config", "details": errors}, ensure_ascii=False, indent=2))
        sys.exit(1)


# ---------------------------------------------------------------------------
# Phase calculation
# ---------------------------------------------------------------------------

def get_phase_key(day, cycle_length, luteal_length, pms_days=7, menstruation_days=5):
    """Return phase key for day (0-indexed from last period start)."""
    menstruation_end = menstruation_days - 1
    ovulation_start = cycle_length - luteal_length - 2
    ovulation_end = cycle_length - luteal_length
    pms_start = cycle_length - pms_days

    if day <= menstruation_end:
        return "menstruation"
    elif day < ovulation_start:
        return "follicular"
    elif day <= ovulation_end:
        return "ovulation"
    elif pms_days > 0 and day >= pms_start:
        return "pms"
    else:
        return "luteal"


def phase_boundary_days(cycle_length, luteal_length, pms_days=7, menstruation_days=5):
    """Return sorted list of (day, phase_key) when each phase starts."""
    boundaries = [
        (0, "menstruation"),
        (menstruation_days, "follicular"),
        (cycle_length - luteal_length - 2, "ovulation"),
        (cycle_length - luteal_length + 1, "luteal"),
    ]
    if pms_days > 0:
        boundaries.append((cycle_length - pms_days, "pms"))
    return sorted(boundaries)


def compute_fertility_window(cycle_length, luteal_length):
    """Compute the fertility window (0-indexed days).

    Returns (fertile_start, peak_start, peak_end, fertile_end) as day numbers.
    - Fertile window: ~5 days before ovulation to 1 day after
    - Peak: ovulation day ± 1
    """
    ovulation_day = cycle_length - luteal_length
    fertile_start = max(0, ovulation_day - 5)
    peak_start = max(0, ovulation_day - 1)
    peak_end = ovulation_day
    fertile_end = ovulation_day + 1
    return fertile_start, peak_start, peak_end, fertile_end


def get_fertility_level(day, cycle_length, luteal_length):
    """Return fertility level string for a given day."""
    fertile_start, peak_start, peak_end, fertile_end = compute_fertility_window(
        cycle_length, luteal_length
    )
    if peak_start <= day <= peak_end:
        return "peak"
    elif fertile_start <= day <= fertile_end:
        return "high"
    elif fertile_start - 2 <= day < fertile_start:
        return "moderate"
    else:
        return "low"


# ---------------------------------------------------------------------------
# Status computation
# ---------------------------------------------------------------------------

def compute_status(config, today=None):
    if today is None:
        today = date.today()

    last = date.fromisoformat(config["last_period_date"])
    cycle_length = config.get("cycle_length", 28)
    luteal_length = config.get("luteal_length", 14)
    pms_days = config.get("pms_days", 7)
    menstruation_days = config.get("menstruation_days", 5)
    lang = config.get("language", "fr")

    days_since = (today - last).days
    if days_since < 0:
        print(json.dumps({"error": "last_period_date is in the future"}))
        sys.exit(1)

    day_in_cycle = days_since % cycle_length
    cycle_number = days_since // cycle_length + 1

    phase_key = get_phase_key(day_in_cycle, cycle_length, luteal_length, pms_days, menstruation_days)
    phase = PHASES[lang][phase_key]

    boundaries = phase_boundary_days(cycle_length, luteal_length, pms_days, menstruation_days)
    next_t = None
    for d, pk in boundaries:
        if d > day_in_cycle:
            next_t = (d, pk)
            break
    if next_t is None:
        days_to_next = cycle_length - day_in_cycle
        next_phase_key = "menstruation"
    else:
        days_to_next = next_t[0] - day_in_cycle
        next_phase_key = next_t[1]

    next_transition_date = today + timedelta(days=days_to_next)
    next_phase = PHASES[lang][next_phase_key]

    # Fertility
    fertility_level = get_fertility_level(day_in_cycle, cycle_length, luteal_length)
    fertile_start, peak_start, peak_end, fertile_end = compute_fertility_window(
        cycle_length, luteal_length
    )
    # Compute absolute dates for current cycle's fertility window
    cycle_start_date = today - timedelta(days=day_in_cycle)
    fertility_window = {
        "current_level": fertility_level,
        "window_start": (cycle_start_date + timedelta(days=fertile_start)).isoformat(),
        "peak_start": (cycle_start_date + timedelta(days=peak_start)).isoformat(),
        "peak_end": (cycle_start_date + timedelta(days=peak_end)).isoformat(),
        "window_end": (cycle_start_date + timedelta(days=fertile_end)).isoformat(),
    }

    return {
        "today": today.isoformat(),
        "cycle_number": cycle_number,
        "day_in_cycle": day_in_cycle + 1,
        "phase": phase_key,
        "phase_name": phase["name"],
        "description": phase["description"],
        "energy": phase["energy"],
        "mood": phase["mood"],
        "fertility": phase["fertility"],
        "fertility_window": fertility_window,
        "tips": phase["tips"],
        "avoid": phase["avoid"],
        "next_transition_date": next_transition_date.isoformat(),
        "next_phase": next_phase_key,
        "next_phase_name": next_phase["name"],
        "days_to_next_transition": days_to_next,
        "language": lang,
    }


# ---------------------------------------------------------------------------
# Cron helpers
# ---------------------------------------------------------------------------

CRON_PREFIX = "cycle-companion-notify"

ALL_PHASE_KEYS = ["menstruation", "follicular", "ovulation", "luteal", "pms"]


def build_cron_payload(config, status):
    """Build the cron job payload for the next phase transition notification."""
    lang = config.get("language", "fr")
    notification_time = config.get("notification_time", "08:00")

    if lang == "fr":
        msg = (
            f"[Cycle Companion] Rappel : demain commence la phase '{status['next_phase_name']}'. "
            f"Lance cycle.py status pour le briefing complet."
        )
    else:
        msg = (
            f"[Cycle Companion] Reminder: tomorrow starts the '{status['next_phase_name']}' phase. "
            f"Run cycle.py status for the full briefing."
        )

    notif_date = date.fromisoformat(status["next_transition_date"]) - timedelta(days=1)
    notif_iso = f"{notif_date.isoformat()}T{notification_time}:00"

    return {
        "name": f"{CRON_PREFIX}-{status['next_phase']}",
        "schedule": {"kind": "at", "at": notif_iso},
        "payload": {"kind": "systemEvent", "text": msg},
        "sessionTarget": "main",
    }


def build_delete_payloads():
    """Build cron deletion payloads for all cycle-companion jobs."""
    return [
        {"name": f"{CRON_PREFIX}-{phase}", "action": "delete"}
        for phase in ALL_PHASE_KEYS
    ]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    # Parse --date before loading config
    sim_date = None
    args = list(sys.argv[1:])
    if "--date" in args:
        idx = args.index("--date")
        if idx + 1 >= len(args):
            print(json.dumps({"error": "Usage: cycle.py --date YYYY-MM-DD <command>"}))
            sys.exit(1)
        try:
            sim_date = date.fromisoformat(args[idx + 1])
        except ValueError:
            print(json.dumps({"error": f"Invalid date: {args[idx + 1]}"}))
            sys.exit(1)
        args.pop(idx)  # remove --date
        args.pop(idx)  # remove the date value

    config = load_config()
    cmd = args[0] if args else "status"

    if cmd == "status":
        print(json.dumps(compute_status(config, today=sim_date), ensure_ascii=False, indent=2))

    elif cmd == "next-transition":
        s = compute_status(config, today=sim_date)
        print(json.dumps({
            "next_transition_date": s["next_transition_date"],
            "next_phase": s["next_phase"],
            "next_phase_name": s["next_phase_name"],
            "days_to_next_transition": s["days_to_next_transition"],
        }, ensure_ascii=False))

    elif cmd == "schedule-cron":
        s = compute_status(config, today=sim_date)
        payload = build_cron_payload(config, s)
        print(json.dumps(payload, ensure_ascii=False, indent=2))

    elif cmd == "delete-cron":
        payloads = build_delete_payloads()
        print(json.dumps(payloads, ensure_ascii=False, indent=2))

    else:
        print(json.dumps({"error": f"Unknown command: {cmd}"}))
        sys.exit(1)


if __name__ == "__main__":
    main()
