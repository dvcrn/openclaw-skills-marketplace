#!/usr/bin/env python3
"""Setup interactif pour work-helper.

Cree la config et les repertoires necessaires.
Usage : python3 setup.py [--cleanup] [--show]
"""

from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

_CONFIG_DIR = Path(os.path.expanduser("~/.openclaw/config/work-helper"))
_CONFIG_PATH = _CONFIG_DIR / "config.json"
_DATA_DIR = Path(os.path.expanduser("~/.openclaw/data/work-helper"))
_SCRIPT_DIR = Path(__file__).resolve().parent
_EXAMPLE_CONFIG = _SCRIPT_DIR.parent / "config.example.json"


def _input_default(prompt: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    val = input(f"{prompt}{suffix}: ").strip()
    return val if val else default


def _input_bool(prompt: str, default: bool = False) -> bool:
    suffix = " [O/n]" if default else " [o/N]"
    val = input(f"{prompt}{suffix}: ").strip().lower()
    if not val:
        return default
    return val in ("o", "oui", "y", "yes", "1", "true")


def setup() -> None:
    print("=== work-helper -- Setup ===\n")

    # charger config existante ou exemple
    cfg = {}
    if _CONFIG_PATH.exists():
        try:
            cfg = json.loads(_CONFIG_PATH.read_text(encoding="utf-8"))
            print(f"Config existante trouvee : {_CONFIG_PATH}")
            if not _input_bool("Reconfigurer ?", default=False):
                print("Setup annule.")
                return
        except (json.JSONDecodeError, OSError):
            pass

    if not cfg and _EXAMPLE_CONFIG.exists():
        cfg = json.loads(_EXAMPLE_CONFIG.read_text(encoding="utf-8"))

    # profil consultant
    print("\n--- Profil consultant ---")
    cfg["consultant_name"] = _input_default(
        "Nom", cfg.get("consultant_name", ""))
    cfg["consultant_role"] = _input_default(
        "Role", cfg.get("consultant_role", "Consultant Sysops / Freelance"))
    cfg["timezone"] = _input_default(
        "Timezone", cfg.get("timezone", "Europe/Paris"))
    cfg["language"] = _input_default(
        "Langue", cfg.get("language", "fr"))

    # projet par defaut
    cfg["default_project"] = _input_default(
        "Projet par defaut (vide = aucun)",
        cfg.get("default_project", ""))

    # CRA
    print("\n--- CRA ---")
    cfg["cra_format"] = _input_default(
        "Format CRA (markdown/table/text)",
        cfg.get("cra_format", "markdown"))

    # LLM
    print("\n--- LLM (recap, CRA, ingestion) ---")
    llm = cfg.get("llm", {})
    llm["enabled"] = _input_bool(
        "Activer le LLM ?", llm.get("enabled", False))

    if llm["enabled"]:
        llm["base_url"] = _input_default(
            "Base URL API", llm.get("base_url", "https://api.openai.com/v1"))
        llm["model"] = _input_default(
            "Modele", llm.get("model", "gpt-4o-mini"))
        llm["api_key_file"] = _input_default(
            "Fichier cle API",
            llm.get("api_key_file", "~/.openclaw/secrets/openai_api_key"))

        # verifier la cle API
        key_path = Path(os.path.expanduser(llm["api_key_file"]))
        if not key_path.exists():
            print(f"\n  Attention : {key_path} n'existe pas.")
            print(f"  Creez ce fichier avec votre cle API.")
            if _input_bool("  Saisir la cle maintenant ?", default=False):
                api_key = input("  Cle API : ").strip()
                if api_key:
                    key_path.parent.mkdir(parents=True, exist_ok=True)
                    key_path.write_text(api_key, encoding="utf-8")
                    os.chmod(str(key_path), 0o600)
                    print(f"  Cle sauvegardee : {key_path} (chmod 600)")

    cfg["llm"] = llm

    # outputs
    print("\n--- Outputs ---")
    outputs = cfg.get("outputs", [])
    if not outputs:
        outputs = [{"type": "file",
                     "path": "~/.openclaw/data/work-helper/exports",
                     "enabled": True}]

    if _input_bool("Configurer export Nextcloud ?", default=False):
        nc_path = _input_default(
            "Chemin Nextcloud", "/Documents/OpenClaw/work-helper")
        # ajouter ou mettre a jour
        nc_found = False
        for o in outputs:
            if o.get("type") == "nextcloud":
                o["path"] = nc_path
                o["enabled"] = True
                nc_found = True
                break
        if not nc_found:
            outputs.append({
                "type": "nextcloud", "path": nc_path, "enabled": True
            })

    if _input_bool("Configurer export email ?", default=False):
        mail_to = _input_default("Email destinataire", "")
        if mail_to:
            mail_found = False
            for o in outputs:
                if o.get("type") == "mail-client":
                    o["mail_to"] = mail_to
                    o["enabled"] = True
                    mail_found = True
                    break
            if not mail_found:
                outputs.append({
                    "type": "mail-client", "mail_to": mail_to, "enabled": True
                })

    cfg["outputs"] = outputs

    # sauvegarder
    _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    _CONFIG_PATH.write_text(
        json.dumps(cfg, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"\nConfig sauvegardee : {_CONFIG_PATH}")

    # creer les repertoires de donnees
    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    (_DATA_DIR / "exports").mkdir(exist_ok=True)
    print(f"Repertoire donnees : {_DATA_DIR}")

    print("\nSetup termine. Lancez init.py pour valider.")


def show() -> None:
    if not _CONFIG_PATH.exists():
        print("Aucune config trouvee. Lancez setup.py d'abord.")
        return
    print(_CONFIG_PATH.read_text(encoding="utf-8"))


def cleanup() -> None:
    print("=== work-helper -- Cleanup ===\n")
    print(f"Config : {_CONFIG_DIR}")
    print(f"Data   : {_DATA_DIR}")
    if not _input_bool("\nSupprimer toutes les donnees work-helper ?",
                       default=False):
        print("Annule.")
        return
    for d in (_CONFIG_DIR, _DATA_DIR):
        if d.exists():
            shutil.rmtree(str(d))
            print(f"Supprime : {d}")
    print("Cleanup termine.")


def main() -> None:
    if "--cleanup" in sys.argv:
        cleanup()
    elif "--show" in sys.argv:
        show()
    else:
        setup()


if __name__ == "__main__":
    main()
