#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
from pathlib import Path


MODE_ORDER = ["morning", "afternoon", "evening", "night"]


def load_json(path: Path):
    return json.loads(path.read_text())


def run_command(command: list[str], apply: bool):
    print(subprocess.list2cmdline(command))
    if not apply:
        return None
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or subprocess.list2cmdline(command))
    stdout = result.stdout.strip()
    return json.loads(stdout) if stdout else None


def load_existing_jobs():
    result = subprocess.run(["openclaw", "cron", "list", "--json"], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "failed to list cron jobs")
    return (json.loads(result.stdout.strip()) or {}).get("jobs", [])


def build_add_command(job: dict) -> list[str]:
    command = [
        "openclaw",
        "cron",
        "add",
        "--name",
        job["name"],
        "--description",
        job["description"],
        "--cron",
        job["cron"],
        "--tz",
        job.get("tz", ""),
        "--system-event",
        job["system_event"],
        "--json",
    ]
    if not job.get("enabled", True):
        command.append("--disabled")
    return command


def build_edit_command(job_id: str, job: dict) -> list[str]:
    command = [
        "openclaw",
        "cron",
        "edit",
        job_id,
        "--name",
        job["name"],
        "--description",
        job["description"],
        "--cron",
        job["cron"],
        "--tz",
        job.get("tz", ""),
        "--system-event",
        job["system_event"],
        "--enable" if job.get("enabled", True) else "--disable",
    ]
    return command


def validate_job(mode: str, payload: dict):
    required = ["name", "description", "cron", "system_event"]
    missing = [field for field in required if not payload.get(field)]
    if missing:
        raise ValueError(f"schedule.cron_jobs.{mode} missing required fields: {', '.join(missing)}")


def main():
    parser = argparse.ArgumentParser(description="Preview or sync cyber-girlfriend cron jobs from config.")
    parser.add_argument("--config", required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    config = load_json(Path(args.config))
    cron_jobs = (((config.get("schedule") or {}).get("cron_jobs")) or {})
    if not cron_jobs:
        raise SystemExit("missing schedule.cron_jobs in config")

    existing = load_existing_jobs()
    jobs_by_id = {job.get("id"): job for job in existing if job.get("id")}
    jobs_by_name = {job.get("name"): job for job in existing if job.get("name")}

    for mode in MODE_ORDER:
        job = cron_jobs.get(mode)
        if not job:
            continue
        validate_job(mode, job)
        existing_job = jobs_by_id.get(job.get("id")) if job.get("id") else None
        if existing_job is None:
            existing_job = jobs_by_name.get(job["name"])

        if existing_job is None:
            print(f"# create {mode}")
            run_command(build_add_command(job), args.apply)
        else:
            print(f"# update {mode} ({existing_job['id']})")
            run_command(build_edit_command(existing_job["id"], job), args.apply)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
