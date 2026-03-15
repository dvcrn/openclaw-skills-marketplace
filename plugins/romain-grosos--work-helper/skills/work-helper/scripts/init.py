#!/usr/bin/env python3
"""Validation de l'installation work-helper.

Verifie :
- Config existe et est valide
- Repertoires de donnees existent
- LLM accessible (si active)
- Skills optionnels (mail-client, nextcloud-files)

Usage : python3 init.py
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

_CONFIG_PATH = Path(os.path.expanduser(
    "~/.openclaw/config/work-helper/config.json"))
_DATA_DIR = Path(os.path.expanduser("~/.openclaw/data/work-helper"))
_SKILLS_DIR = Path(os.path.expanduser("~/.openclaw/workspace/skills"))


def _check(name: str, ok: bool, detail: str = "") -> bool:
    status = "PASS" if ok else "FAIL"
    msg = f"  [{status}] {name}"
    if detail:
        msg += f" -- {detail}"
    print(msg)
    return ok


def _check_skip(name: str, detail: str = "") -> None:
    msg = f"  [SKIP] {name}"
    if detail:
        msg += f" -- {detail}"
    print(msg)


def main() -> None:
    print("=== work-helper -- Validation ===\n")
    all_ok = True

    # 1. config
    print("Configuration :")
    if not _CONFIG_PATH.exists():
        _check("config.json", False, "fichier introuvable")
        print("\n  Lancez d'abord : python3 setup.py")
        sys.exit(1)

    try:
        cfg = json.loads(_CONFIG_PATH.read_text(encoding="utf-8"))
        _check("config.json", True, str(_CONFIG_PATH))
    except json.JSONDecodeError as exc:
        _check("config.json", False, f"JSON invalide : {exc}")
        sys.exit(1)

    _check("consultant_name",
           bool(cfg.get("consultant_name")),
           cfg.get("consultant_name", "(vide)"))

    _check("timezone",
           bool(cfg.get("timezone")),
           cfg.get("timezone", "(vide)"))

    # 2. data directories
    print("\nRepertoires :")
    all_ok &= _check("data_dir", _DATA_DIR.exists(), str(_DATA_DIR))
    exports_dir = _DATA_DIR / "exports"
    all_ok &= _check("exports_dir", exports_dir.exists(), str(exports_dir))

    # 3. LLM
    print("\nLLM :")
    llm = cfg.get("llm", {})
    if not llm.get("enabled"):
        _check_skip("LLM", "desactive dans la config")
    else:
        # verifier la cle API
        key_file = os.path.expanduser(llm.get("api_key_file", ""))
        api_key = ""
        if key_file and os.path.isfile(key_file):
            api_key = Path(key_file).read_text(encoding="utf-8").strip()
            _check("api_key_file", True, key_file)
        else:
            api_key = os.environ.get("OPENAI_API_KEY", "")
            if api_key:
                _check("api_key (env)", True, "OPENAI_API_KEY definie")
            else:
                all_ok &= _check("api_key", False,
                                  f"ni {key_file} ni OPENAI_API_KEY")

        if api_key:
            # test de connectivite
            base_url = llm.get("base_url", "https://api.openai.com/v1").rstrip("/")
            url = f"{base_url}/models"
            req = urllib.request.Request(
                url,
                headers={"Authorization": f"Bearer {api_key}"},
            )
            try:
                with urllib.request.urlopen(req, timeout=10) as resp:
                    _check("LLM connectivity", resp.status == 200,
                           f"{base_url} OK")
            except urllib.error.HTTPError as exc:
                # 401/403 = cle invalide, autre = reseau
                if exc.code in (401, 403):
                    all_ok &= _check("LLM connectivity", False,
                                      f"authentification echouee ({exc.code})")
                else:
                    _check("LLM connectivity", True,
                           f"API accessible (HTTP {exc.code})")
            except (urllib.error.URLError, OSError) as exc:
                all_ok &= _check("LLM connectivity", False, str(exc))

    # 4. optional skills
    print("\nSkills optionnels :")
    for skill_name, script_name in [
        ("mail-client", "mail.py"),
        ("nextcloud-files", "nextcloud.py"),
    ]:
        script = _SKILLS_DIR / skill_name / "scripts" / script_name
        if script.is_file():
            _check(skill_name, True, "installe")
        else:
            _check_skip(skill_name, "non installe (optionnel)")

    # result
    print()
    if all_ok:
        print("Validation terminee : tout OK.")
    else:
        print("Validation terminee avec des erreurs.")
        print("Corrigez les problemes ci-dessus puis relancez init.py.")
        sys.exit(1)


if __name__ == "__main__":
    main()
