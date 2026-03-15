#!/usr/bin/env python3
"""work-helper -- assistant de travail personnel.

Sous-commandes :
  log      Journal d'activite
  note     Notes libres
  remind   Rappels (crons OpenClaw)
  recap    Recapitulatifs LLM
  cra      Compte Rendu d'Activite
  ingest   Ingestion PDF reMarkable
  status   Vue synthetique
  export   Export (nextcloud, email, fichier)

Usage :
  python3 work_helper.py <command> <subcommand> [options]
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Optional

# ── paths ────────────────────────────────────────────────────────────

_CONFIG_DIR = Path(os.path.expanduser("~/.openclaw/config/work-helper"))
_CONFIG_PATH = _CONFIG_DIR / "config.json"
_DATA_DIR = Path(os.path.expanduser("~/.openclaw/data/work-helper"))
_REMINDERS_PATH = _DATA_DIR / "reminders.json"
_PROJECTS_PATH = _DATA_DIR / "projects.json"
_SKILLS_DIR = Path(os.path.expanduser("~/.openclaw/workspace/skills"))

_DEFAULT_CONFIG = {
    "language": "fr",
    "timezone": "Europe/Paris",
    "consultant_name": "",
    "consultant_role": "Consultant Sysops / Freelance",
    "default_project": "",
    "cra_format": "markdown",
    "cra_week_days": ["lundi", "mardi", "mercredi", "jeudi", "vendredi"],
    "ingest_mode": "meeting",
    "llm": {
        "enabled": False,
        "base_url": "https://api.openai.com/v1",
        "api_key_file": "~/.openclaw/secrets/openai_api_key",
        "model": "gpt-4o-mini",
        "max_tokens": 2048,
    },
    "outputs": [],
}


# ── config ───────────────────────────────────────────────────────────

def _load_config() -> dict:
    cfg = dict(_DEFAULT_CONFIG)
    cfg["llm"] = dict(_DEFAULT_CONFIG["llm"])
    if _CONFIG_PATH.exists():
        try:
            user_cfg = json.loads(_CONFIG_PATH.read_text(encoding="utf-8"))
            if "llm" in user_cfg:
                cfg["llm"].update(user_cfg.pop("llm"))
            cfg.update(user_cfg)
        except (json.JSONDecodeError, OSError):
            pass
    return cfg


# ── reminders store ──────────────────────────────────────────────────

def _load_reminders() -> List[dict]:
    if not _REMINDERS_PATH.exists():
        return []
    try:
        return json.loads(_REMINDERS_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def _save_reminders(reminders: List[dict]) -> None:
    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    import tempfile
    tmp_fd, tmp_path = tempfile.mkstemp(dir=str(_DATA_DIR), suffix=".tmp")
    try:
        with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
            json.dump(reminders, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, str(_REMINDERS_PATH))
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


# ── projects store ───────────────────────────────────────────────────

def _load_projects() -> List[dict]:
    if not _PROJECTS_PATH.exists():
        return []
    try:
        return json.loads(_PROJECTS_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def _extract_active_projects(entries: List[dict]) -> List[str]:
    """Extrait les projets actifs des entrees recentes."""
    projects = set()
    cutoff = datetime.now(timezone.utc) - timedelta(days=30)
    for e in entries:
        if e.get("project"):
            try:
                ts = datetime.fromisoformat(e["timestamp"])
                if ts >= cutoff:
                    projects.add(e["project"])
            except (ValueError, KeyError):
                projects.add(e["project"])
    return sorted(projects)


# ── formatting ───────────────────────────────────────────────────────

def _fmt_entry(e: dict) -> str:
    ts = e["timestamp"][:16].replace("T", " ")
    parts = [f"[{ts}]"]
    if e.get("project"):
        parts.append(f"({e['project']})")
    if e.get("duration_minutes"):
        h, m = divmod(e["duration_minutes"], 60)
        dur = f"{h}h{m:02d}" if h else f"{m}min"
        parts.append(f"[{dur}]")
    parts.append(e["text"])
    if e.get("tags"):
        parts.append(f"  #{', #'.join(e['tags'])}")
    return " ".join(parts)


def _fmt_note(n: dict) -> str:
    ts = n["timestamp"][:16].replace("T", " ")
    proj = f" ({n['project']})" if n.get("project") else ""
    return f"[{ts}]{proj} {n['text']}"


def _fmt_reminder(r: dict) -> str:
    sched = r.get("schedule", "")
    status = " [recurrent]" if r.get("recurring") else ""
    return f"[{r['id']}] {r['text']} -- {sched}{status}"


# ── commands: log ────────────────────────────────────────────────────

def cmd_log(args: argparse.Namespace, cfg: dict) -> None:
    import _journal

    if args.log_action == "add":
        entry = _journal.add(
            args.text,
            project=args.project or cfg.get("default_project", ""),
            duration=args.duration or "",
            tags=args.tags or "",
        )
        print(json.dumps(entry, ensure_ascii=False, indent=2))

    elif args.log_action in ("today", "week", "month"):
        entries = _journal.list_entries(period=args.log_action)
        if not entries:
            print(f"Aucune entree ({args.log_action}).")
            return
        for e in entries:
            print(_fmt_entry(e))
        # total duree
        total = sum(e.get("duration_minutes") or 0 for e in entries)
        if total:
            h, m = divmod(total, 60)
            print(f"\nTotal : {h}h{m:02d} ({len(entries)} entrees)")
        else:
            print(f"\n{len(entries)} entrees")

    elif args.log_action == "search":
        results = _journal.search(args.term)
        if not results:
            print(f"Aucun resultat pour '{args.term}'.")
            return
        for e in results:
            print(_fmt_entry(e))
        print(f"\n{len(results)} resultats")

    elif args.log_action == "delete":
        if _journal.delete(args.id):
            print(f"Entree {args.id} supprimee.")
        else:
            print(f"Entree {args.id} introuvable.")

    else:
        print("Usage: work_helper.py log {add|today|week|month|search|delete}")


# ── commands: note ───────────────────────────────────────────────────

def cmd_note(args: argparse.Namespace, cfg: dict) -> None:
    import _notes

    if args.note_action == "add":
        note = _notes.add(args.text, project=args.project or "")
        print(json.dumps(note, ensure_ascii=False, indent=2))

    elif args.note_action == "list":
        notes = _notes.list_notes(project=args.project or "")
        if not notes:
            print("Aucune note.")
            return
        for n in notes:
            print(_fmt_note(n))

    elif args.note_action == "search":
        results = _notes.search(args.term)
        if not results:
            print(f"Aucun resultat pour '{args.term}'.")
            return
        for n in results:
            print(_fmt_note(n))

    elif args.note_action == "delete":
        if _notes.delete(args.id):
            print(f"Note {args.id} supprimee.")
        else:
            print(f"Note {args.id} introuvable.")

    else:
        print("Usage: work_helper.py note {add|list|search|delete}")


# ── commands: remind ─────────────────────────────────────────────────

_DAY_MAP = {
    "monday": "1", "tuesday": "2", "wednesday": "3", "thursday": "4",
    "friday": "5", "saturday": "6", "sunday": "0",
    "lundi": "1", "mardi": "2", "mercredi": "3", "jeudi": "4",
    "vendredi": "5", "samedi": "6", "dimanche": "0",
}


def cmd_remind(args: argparse.Namespace, cfg: dict) -> None:
    if args.remind_action == "add":
        import uuid
        reminder = {
            "id": uuid.uuid4().hex[:8],
            "text": args.text,
            "recurring": bool(args.every),
        }

        time_parts = (args.time or "09:00").split(":")
        hour = int(time_parts[0])
        minute = int(time_parts[1]) if len(time_parts) > 1 else 0

        if args.every:
            # recurrent: --every friday
            day_key = args.every.lower()
            day_num = _DAY_MAP.get(day_key)
            if not day_num:
                print(f"Jour inconnu : {args.every}")
                print(f"Jours valides : {', '.join(sorted(_DAY_MAP.keys()))}")
                sys.exit(1)
            cron_expr = f"{minute} {hour} * * {day_num}"
            reminder["schedule"] = f"every {args.every} {hour:02d}:{minute:02d}"
        elif args.date:
            # one-shot: --date 2026-03-15
            dt = datetime.strptime(args.date, "%Y-%m-%d")
            cron_expr = f"{minute} {hour} {dt.day} {dt.month} *"
            reminder["schedule"] = f"{args.date} {hour:02d}:{minute:02d}"
        else:
            print("Erreur : --date ou --every requis")
            sys.exit(1)

        reminder["cron_expression"] = cron_expr

        # sauvegarder localement
        reminders = _load_reminders()
        reminders.append(reminder)
        _save_reminders(reminders)

        # emettre le payload cron pour l'agent OpenClaw (systemEvent)
        tz = cfg.get("timezone", "Europe/Paris")

        if args.every:
            schedule = {"kind": "cron", "cron": cron_expr, "timezone": tz}
        else:
            # one-shot : date ISO
            dt_str = f"{args.date}T{hour:02d}:{minute:02d}:00"
            schedule = {"kind": "at", "at": dt_str}

        cron_payload = {
            "name": f"work-helper-remind-{reminder['id']}",
            "schedule": schedule,
            "payload": {
                "kind": "systemEvent",
                "text": f"[Rappel work-helper] {args.text}",
            },
            "sessionTarget": "main",
        }

        print(json.dumps({
            "reminder": reminder,
            "cron_payload": cron_payload,
        }, ensure_ascii=False, indent=2))

    elif args.remind_action == "list":
        reminders = _load_reminders()
        if not reminders:
            print("Aucun rappel.")
            return
        for r in reminders:
            print(_fmt_reminder(r))

    elif args.remind_action == "cancel":
        reminders = _load_reminders()
        new = [r for r in reminders if r["id"] != args.id]
        if len(new) == len(reminders):
            print(f"Rappel {args.id} introuvable.")
            return
        _save_reminders(new)
        # emettre le payload de suppression cron
        print(json.dumps({
            "status": "cancelled",
            "id": args.id,
            "cron_delete": {
                "name": f"work-helper-remind-{args.id}",
            },
        }, ensure_ascii=False, indent=2))

    else:
        print("Usage: work_helper.py remind {add|list|cancel}")


# ── commands: recap ──────────────────────────────────────────────────

def cmd_recap(args: argparse.Namespace, cfg: dict) -> None:
    import _journal
    import _llm

    if not cfg["llm"].get("enabled"):
        print("Erreur : LLM non active dans la config (llm.enabled = false)")
        sys.exit(1)

    entries = _journal.list_entries(period=args.period)
    result = _llm.recap(
        entries, args.period, cfg["llm"],
        consultant_name=cfg.get("consultant_name", ""),
        consultant_role=cfg.get("consultant_role", ""),
    )
    print(result)


# ── commands: cra ────────────────────────────────────────────────────

def cmd_cra(args: argparse.Namespace, cfg: dict) -> None:
    import _journal
    import _llm

    if not cfg["llm"].get("enabled"):
        print("Erreur : LLM non active dans la config (llm.enabled = false)")
        sys.exit(1)

    entries = _journal.list_entries(period=args.period)
    fmt = args.format or cfg.get("cra_format", "markdown")
    result = _llm.cra(
        entries, args.period, cfg["llm"],
        format_=fmt,
        consultant_name=cfg.get("consultant_name", ""),
        consultant_role=cfg.get("consultant_role", ""),
        week_days=cfg.get("cra_week_days"),
    )
    print(result)


# ── commands: ingest ─────────────────────────────────────────────────

def cmd_ingest(args: argparse.Namespace, cfg: dict) -> None:
    import _ingest
    import _llm

    if not cfg["llm"].get("enabled"):
        print("Erreur : LLM non active dans la config (llm.enabled = false)")
        sys.exit(1)

    mode = args.mode or cfg.get("ingest_mode", "meeting")
    project = args.project or cfg.get("default_project", "")

    # etape 1 : recuperer le PDF
    if args.pdf:
        pdf_path = args.pdf
        subject = Path(pdf_path).stem
    else:
        print("Recherche du dernier email avec PJ PDF...")
        subject, pdf_path = _ingest.fetch_latest_pdf_email()
        if pdf_path is None:
            print(f"Erreur : {subject}")
            sys.exit(1)
        print(f"Email trouve : {subject}")
        print(f"PDF : {pdf_path}")

    # etape 2 : transcription via API Vision (direct, sans agent)
    print(f"Transcription du PDF via Vision API...")
    try:
        transcription = _llm.read_pdf_vision(pdf_path, cfg["llm"])
    except Exception as exc:
        print(f"Erreur transcription Vision : {exc}")
        sys.exit(1)

    print(f"Transcription OK ({len(transcription)} caracteres)")

    # etape 3 : structuration LLM selon le mode
    print(f"Structuration ({mode})...")
    result = _llm.ingest_transcription(transcription, mode, cfg["llm"])
    output = _ingest.build_ingest_output(
        mode, result, project=project, subject=subject
    )

    # etape 4 : auto-stockage selon le mode
    if mode == "log" and output.get("entries"):
        count = _ingest.auto_log_entries(output["entries"], project)
        output["auto_logged"] = count
        print(f"{count} entrees ajoutees au journal.")
    elif mode == "notes":
        note = _ingest.auto_note_content(result, project=project)
        output["note_id"] = note["id"]
        print(f"Note creee : {note['id']}")
    else:
        # meeting, cra : afficher le resultat structure
        print(result)

    # emettre le JSON complet sur stderr pour l'agent/logs
    print(json.dumps(output, ensure_ascii=False, indent=2), file=sys.stderr)


# ── commands: status ─────────────────────────────────────────────────

def cmd_status(args: argparse.Namespace, cfg: dict) -> None:
    import _journal
    import _notes

    print("=== Work Helper -- Status ===\n")

    # projets actifs
    entries_all = _journal.get_all()
    projects = _extract_active_projects(entries_all)
    print(f"Projets actifs (30j) : {', '.join(projects) if projects else 'aucun'}")

    # entrees du jour
    today_entries = _journal.list_entries(period="today")
    print(f"\nJournal aujourd'hui : {len(today_entries)} entrees")
    for e in today_entries[-5:]:  # max 5 dernieres
        print(f"  {_fmt_entry(e)}")

    # temps cette semaine
    week_entries = _journal.list_entries(period="week")
    week_total = sum(e.get("duration_minutes") or 0 for e in week_entries)
    if week_total:
        h, m = divmod(week_total, 60)
        print(f"\nTemps cette semaine : {h}h{m:02d} ({len(week_entries)} entrees)")
    else:
        print(f"\nCette semaine : {len(week_entries)} entrees (pas de durees renseignees)")

    # notes recentes
    notes = _notes.list_notes()
    if notes:
        print(f"\nDernieres notes ({len(notes)} total) :")
        for n in notes[-3:]:
            print(f"  {_fmt_note(n)}")

    # rappels
    reminders = _load_reminders()
    if reminders:
        print(f"\nRappels actifs ({len(reminders)}) :")
        for r in reminders:
            print(f"  {_fmt_reminder(r)}")


# ── commands: export ─────────────────────────────────────────────────

def cmd_export(args: argparse.Namespace, cfg: dict) -> None:
    import _journal

    period = args.period or "week"
    entries = _journal.list_entries(period=period)
    if not entries:
        print(f"Aucune entree a exporter ({period}).")
        return

    # formater en markdown
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M")
    lines = [f"# Journal work-helper -- {period} ({now})\n"]
    for e in entries:
        lines.append(_fmt_entry(e))
    content = "\n".join(lines) + "\n"

    if args.export_target == "nextcloud":
        nc_script = _SKILLS_DIR / "nextcloud-files" / "scripts" / "nextcloud.py"
        if not nc_script.is_file():
            print("Erreur : skill nextcloud-files non installe")
            sys.exit(1)
        # trouver le path de destination
        nc_path = None
        for o in cfg.get("outputs", []):
            if o.get("type") == "nextcloud" and o.get("enabled"):
                nc_path = o.get("path", "")
                break
        if not nc_path:
            nc_path = "/Documents/OpenClaw/work-helper"

        filename = f"journal_{period}_{now}.md"
        dest = f"{nc_path}/{filename}"

        result = subprocess.run(
            [sys.executable, str(nc_script),
             "write", dest],
            input=content, capture_output=True, text=True, timeout=60,
        )
        if result.returncode == 0:
            print(f"Exporte vers Nextcloud : {dest}")
        else:
            print(f"Erreur Nextcloud : {result.stderr.strip()}")

    elif args.export_target == "email":
        mail_script = _SKILLS_DIR / "mail-client" / "scripts" / "mail.py"
        if not mail_script.is_file():
            print("Erreur : skill mail-client non installe")
            sys.exit(1)
        to = args.to
        if not to:
            for o in cfg.get("outputs", []):
                if o.get("type") == "mail-client" and o.get("enabled"):
                    to = o.get("mail_to", "")
                    break
        if not to:
            print("Erreur : destinataire requis (--to)")
            sys.exit(1)

        subject = f"Journal work-helper -- {period} ({now})"
        result = subprocess.run(
            [sys.executable, str(mail_script),
             "send", "--to", to, "--subject", subject, "--body", content],
            capture_output=True, text=True, timeout=60,
        )
        if result.returncode == 0:
            print(f"Envoye par email a : {to}")
        else:
            print(f"Erreur email : {result.stderr.strip()}")

    elif args.export_target == "file":
        export_dir = Path(os.path.expanduser(
            "~/.openclaw/data/work-helper/exports"
        ))
        export_dir.mkdir(parents=True, exist_ok=True)
        filename = f"journal_{period}_{now}.md"
        dest = export_dir / filename
        dest.write_text(content, encoding="utf-8")
        print(f"Exporte : {dest}")

    else:
        print("Usage: work_helper.py export {nextcloud|email|file}")


# ── argument parser ──────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="work_helper",
        description="Assistant de travail personnel -- OpenClaw skill",
    )
    sub = parser.add_subparsers(dest="command")

    # ── log ──
    p_log = sub.add_parser("log", help="Journal d'activite")
    log_sub = p_log.add_subparsers(dest="log_action")

    p_log_add = log_sub.add_parser("add", help="Ajouter une entree")
    p_log_add.add_argument("text", help="Description de l'activite")
    p_log_add.add_argument("--project", "-p", default="")
    p_log_add.add_argument("--duration", "-d", default="")
    p_log_add.add_argument("--tags", "-t", default="")

    for period in ("today", "week", "month"):
        log_sub.add_parser(period, help=f"Entrees du {period}")

    p_log_search = log_sub.add_parser("search", help="Rechercher")
    p_log_search.add_argument("term")

    p_log_del = log_sub.add_parser("delete", help="Supprimer une entree")
    p_log_del.add_argument("id")

    # ── note ──
    p_note = sub.add_parser("note", help="Notes libres")
    note_sub = p_note.add_subparsers(dest="note_action")

    p_note_add = note_sub.add_parser("add", help="Ajouter une note")
    p_note_add.add_argument("text")
    p_note_add.add_argument("--project", "-p", default="")

    p_note_list = note_sub.add_parser("list", help="Lister les notes")
    p_note_list.add_argument("--project", "-p", default="")

    p_note_search = note_sub.add_parser("search", help="Rechercher")
    p_note_search.add_argument("term")

    p_note_del = note_sub.add_parser("delete", help="Supprimer")
    p_note_del.add_argument("id")

    # ── remind ──
    p_remind = sub.add_parser("remind", help="Rappels")
    remind_sub = p_remind.add_subparsers(dest="remind_action")

    p_remind_add = remind_sub.add_parser("add", help="Creer un rappel")
    p_remind_add.add_argument("text")
    p_remind_add.add_argument("--date", default="")
    p_remind_add.add_argument("--time", default="09:00")
    p_remind_add.add_argument("--every", default="")

    remind_sub.add_parser("list", help="Lister les rappels")

    p_remind_cancel = remind_sub.add_parser("cancel", help="Annuler")
    p_remind_cancel.add_argument("id")

    # ── recap ──
    p_recap = sub.add_parser("recap", help="Recapitulatif LLM")
    p_recap.add_argument("period", choices=["today", "week", "month"])

    # ── cra ──
    p_cra = sub.add_parser("cra", help="Compte Rendu d'Activite")
    p_cra.add_argument("period", choices=["week", "month"])
    p_cra.add_argument("--format", choices=["markdown", "table", "text"],
                       default="")

    # ── ingest ──
    p_ingest = sub.add_parser("ingest", help="Ingestion PDF reMarkable")
    p_ingest.add_argument("--mode", "-m",
                          choices=["meeting", "log", "notes", "cra"],
                          default="")
    p_ingest.add_argument("--project", "-p", default="")
    p_ingest.add_argument("--pdf", default="",
                          help="Chemin PDF (sinon recupere via mail)")

    # ── status ──
    sub.add_parser("status", help="Vue synthetique")

    # ── export ──
    p_export = sub.add_parser("export", help="Exporter")
    export_sub = p_export.add_subparsers(dest="export_target")

    p_exp_nc = export_sub.add_parser("nextcloud")
    p_exp_nc.add_argument("--period", default="week")

    p_exp_mail = export_sub.add_parser("email")
    p_exp_mail.add_argument("--to", default="")
    p_exp_mail.add_argument("--period", default="week")

    p_exp_file = export_sub.add_parser("file")
    p_exp_file.add_argument("--period", default="week")

    return parser


# ── main ─────────────────────────────────────────────────────────────

def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    cfg = _load_config()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    dispatch = {
        "log": cmd_log,
        "note": cmd_note,
        "remind": cmd_remind,
        "recap": cmd_recap,
        "cra": cmd_cra,
        "ingest": cmd_ingest,
        "status": cmd_status,
        "export": cmd_export,
    }

    handler = dispatch.get(args.command)
    if handler:
        handler(args, cfg)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
