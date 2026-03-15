#!/usr/bin/env python3
"""
Bootstrap secure identity material for Apple Health sync.
"""

import argparse
import json
import os
import secrets
import shutil
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

DEFAULT_SUPABASE_GET_DATA_URL = "https://snpiylxajnxpklpwdtdg.supabase.co/functions/v1/get-data"
DEFAULT_SUPABASE_PUBLISHABLE_KEY = "sb_publishable_HW9XhDFQLrcPoGsbYIz7zg_FnFOePtQ"
DEFAULT_IOS_APP_LINK = "https://apps.apple.com/app/health-sync-for-openclaw/id6759522298"
STATE_DIR = Path.home() / ".apple-health-sync"
CONFIG_DIR = STATE_DIR / "config"
SECRETS_DIR = CONFIG_DIR / "secrets"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def run_checked(command: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def secure_json_write(path: Path, value: Dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    os.chmod(tmp_path, 0o600)
    tmp_path.replace(path)


def generate_record_id() -> str:
    return "ahs_" + secrets.token_urlsafe(16).rstrip("=")


def generate_write_token() -> str:
    return secrets.token_urlsafe(32).rstrip("=")


def ensure_binary(binary_name: str) -> None:
    if shutil.which(binary_name) is None:
        raise RuntimeError(f"Missing required binary: {binary_name}")


def generate_keys(
    private_key_path: Path,
    public_key_path: Path,
    rotate: bool,
    algorithm: str,
) -> str:
    private_exists = private_key_path.exists()
    public_exists = public_key_path.exists()
    if private_exists or public_exists:
        if private_exists and public_exists and not rotate:
            return "existing"
        if not rotate:
            raise RuntimeError("Only one key file exists. Fix manually or run with --rotate.")
        private_key_path.unlink(missing_ok=True)
        public_key_path.unlink(missing_ok=True)

    if algorithm == "rsa-2048":
        run_checked(
            [
                "openssl",
                "genpkey",
                "-algorithm",
                "RSA",
                "-pkeyopt",
                "rsa_keygen_bits:2048",
                "-out",
                str(private_key_path),
            ]
        )
    else:
        run_checked(["openssl", "genpkey", "-algorithm", "ED25519", "-out", str(private_key_path)])

    run_checked(["openssl", "pkey", "-in", str(private_key_path), "-pubout", "-out", str(public_key_path)])
    os.chmod(private_key_path, 0o600)
    os.chmod(public_key_path, 0o644)
    return "generated"


def public_key_base64_from_pem(public_key_pem: str) -> str:
    body = (
        public_key_pem.replace("-----BEGIN PUBLIC KEY-----", "")
        .replace("-----END PUBLIC KEY-----", "")
        .replace("\n", "")
        .replace("\r", "")
        .strip()
    )
    if not body:
        raise RuntimeError("Generated public key PEM is empty.")
    return body


def ensure_sqlite_schema(sqlite_path: Path) -> None:
    sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(sqlite_path)
    try:
        conn.execute(
            """
            create table if not exists health_data (
              id integer primary key autoincrement,
              user_id text not null,
              date text not null,
              data text not null,
              created_at text not null,
              updated_at text not null
            );
            """
        )
        conn.execute(
            "create unique index if not exists health_data_user_date_idx "
            "on health_data (user_id, date);"
        )
        conn.commit()
    finally:
        conn.close()


def render_qr(payload: str, config_dir: Path) -> Optional[Path]:
    qr_png_path = config_dir / "registration-qr.png"

    if shutil.which("qrencode"):
        subprocess.run(["qrencode", "-t", "ANSIUTF8", payload], check=True)
        subprocess.run(["qrencode", "-o", str(qr_png_path), payload], check=True)
        return qr_png_path

    try:
        import qrcode
    except ImportError:
        print("QR rendering skipped: install 'qrencode' or Python package 'qrcode'.")
        return None

    qr = qrcode.QRCode(border=1)
    qr.add_data(payload)
    qr.make(fit=True)
    qr.print_ascii(invert=True)

    try:
        image = qr.make_image(fill_color="black", back_color="white")
        image.save(qr_png_path)
        return qr_png_path
    except Exception:
        print("QR PNG generation skipped: qrcode backend has no image support.")
        return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize keypair and config for HealthSync.")
    parser.add_argument(
        "--state-dir",
        default="",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--record-id",
        help="Optional fixed ID. If omitted, a secure random ID is generated.",
    )
    parser.add_argument(
        "--algorithm",
        choices=("rsa-2048", "ed25519"),
        default="rsa-2048",
        help="Key algorithm. Use rsa-2048 when iOS data encryption is required.",
    )
    parser.add_argument(
        "--storage",
        choices=("auto", "sqlite", "json", "custom"),
        default="auto",
        help="Default local storage backend for fetch script.",
    )
    parser.add_argument(
        "--custom-sink-command",
        default="",
        help="Optional command for storage='custom'. JSON payload is passed via stdin.",
    )
    parser.add_argument(
        "--rotate",
        action="store_true",
        help="Rotate keys if key files already exist.",
    )
    return parser.parse_args()


def main() -> int:
    os.umask(0o077)
    args = parse_args()
    state_dir = STATE_DIR.expanduser().resolve()
    if args.state_dir:
        requested_dir = Path(args.state_dir).expanduser().resolve()
        if requested_dir != state_dir:
            print(f"Ignoring --state-dir={requested_dir}; using fixed path {state_dir}.")
    state_dir.mkdir(parents=True, exist_ok=True)
    config_dir = CONFIG_DIR.expanduser().resolve()
    config_dir.mkdir(parents=True, exist_ok=True)
    secrets_dir = SECRETS_DIR.expanduser().resolve()
    secrets_dir.mkdir(parents=True, exist_ok=True)

    try:
        ensure_binary("openssl")
    except RuntimeError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    private_key_path = secrets_dir / "private_key.pem"
    public_key_path = config_dir / "public_key.pem"
    config_path = config_dir / "config.json"
    qr_payload_path = config_dir / "registration-qr.json"

    existing_config: Dict = {}
    if config_path.exists():
        existing_config = json.loads(config_path.read_text(encoding="utf-8"))

    record_id = args.record_id or existing_config.get("record_id") or generate_record_id()
    existing_write_token = str(existing_config.get("write_token", "")).strip()
    write_token = generate_write_token() if args.rotate or not existing_write_token else existing_write_token
    resolved_get_data_url = DEFAULT_SUPABASE_GET_DATA_URL

    try:
        generate_keys(private_key_path, public_key_path, rotate=args.rotate, algorithm=args.algorithm)
    except RuntimeError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    except subprocess.CalledProcessError as error:
        print(error.stderr.decode("utf-8", errors="replace"), file=sys.stderr)
        return 1

    public_key_pem = public_key_path.read_text(encoding="utf-8")
    public_key_base64 = public_key_base64_from_pem(public_key_pem)
    qr_payload = {
        "v": 3,
        "id": record_id,
        "alg": "RSA-2048" if args.algorithm == "rsa-2048" else "Ed25519",
        "publicKeyBase64": public_key_base64,
        "writeToken": write_token,
    }
    qr_payload_compact = json.dumps(qr_payload, separators=(",", ":"))
    secure_json_write(qr_payload_path, qr_payload)

    qr_png_path = None
    try:
        qr_png_path = render_qr(qr_payload_compact, config_dir)
    except subprocess.CalledProcessError as error:
        message = error.stderr.decode("utf-8", errors="replace") if error.stderr else str(error)
        print(f"QR rendering failed: {message}")

    resolved_storage = args.storage if args.storage != "auto" else existing_config.get("storage", "sqlite")
    resolved_custom_sink = (
        args.custom_sink_command
        if args.custom_sink_command
        else existing_config.get("custom_sink_command", "")
    )
    sqlite_path = state_dir / "health_data.db"
    ensure_sqlite_schema(sqlite_path)

    config = {
        "record_id": record_id,
        "algorithm": "RSA-2048" if args.algorithm == "rsa-2048" else "Ed25519",
        "state_dir": str(state_dir),
        "config_dir": str(config_dir),
        "secrets_dir": str(secrets_dir),
        "private_key_path": str(private_key_path),
        "public_key_path": str(public_key_path),
        "public_key_base64": public_key_base64,
        "write_token": write_token,
        "supabase_get_data_url": resolved_get_data_url,
        "supabase_publishable_key": DEFAULT_SUPABASE_PUBLISHABLE_KEY,
        "ios_app_link": DEFAULT_IOS_APP_LINK,
        "storage": resolved_storage,
        "custom_sink_command": resolved_custom_sink,
        "sqlite_path": str(sqlite_path),
        "json_path": str(config_dir / "health_data.ndjson"),
        "qr_payload_path": str(qr_payload_path),
        "qr_png_path": str(qr_png_path) if qr_png_path else "",
        "updated_at": now_iso(),
    }
    secure_json_write(config_path, config)

    print("\nInitialization complete.")
    print(f"State dir: {state_dir}")
    print(f"Config dir: {config_dir}")
    print(f"Secrets dir: {secrets_dir}")
    print(f"Record ID: {record_id}")
    print(f"Private key: {private_key_path}")
    print(f"Public key: {public_key_path}")
    print(f"QR payload: {qr_payload_path}")
    if qr_png_path:
        print(f"QR PNG: {qr_png_path}")
    print(f"iOS app link: {DEFAULT_IOS_APP_LINK}")

    print("\nCopyable values")
    print("USER_ID")
    print(record_id)
    print("\nPUBLIC_KEY")
    print(public_key_base64)
    print("\nWRITE_TOKEN")
    print(write_token)

    print("\nCronJobs are managed by OpenClaw, not by this script.")
    print("\nShare only USER_ID + PUBLIC_KEY + WRITE_TOKEN/QR with iOS onboarding.")
    print("Never share private_key.pem.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
