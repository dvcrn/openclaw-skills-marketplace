"""Pipeline ingestion reMarkable : mail -> PDF -> Vision -> structuration.

Sequence :
1. Appelle mail-client pour recuperer le dernier email avec PJ PDF
2. Sauvegarde le PDF localement
3. Envoie le PDF a l'API Vision (base64) pour transcription
4. Envoie la transcription au LLM pour structuration (via _llm.py)
5. Selon le mode, stocke dans journal ou notes

Dependencies :
- mail-client skill (subprocess, optionnel si PDF fourni directement)
- API LLM compatible Vision (OpenAI GPT-4o, Anthropic Claude, etc.)
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple

_DATA_DIR = Path(os.path.expanduser("~/.openclaw/data/work-helper"))
_SKILLS_DIR = Path(os.path.expanduser("~/.openclaw/workspace/skills"))


def _find_skill_script(skill: str, script: str) -> Path:
    """Localise un script dans un skill installe."""
    path = _SKILLS_DIR / skill / "scripts" / script
    if not path.is_file():
        raise FileNotFoundError(
            f"Script introuvable : {path}\n"
            f"Le skill '{skill}' est-il installe ?"
        )
    # securite : verifier qu'on reste dans le repertoire skills
    resolved = path.resolve()
    if not str(resolved).startswith(str(_SKILLS_DIR.resolve())):
        raise ValueError(f"Chemin suspect hors du repertoire skills : {resolved}")
    return path


def fetch_latest_pdf_email() -> Tuple[str, Optional[str]]:
    """Recupere le dernier email avec PJ PDF via mail-client.

    Utilise mail-client search (--query) puis read pour obtenir le contenu.
    Les pieces jointes sont retournees en base64 dans le JSON de read.
    Le PDF est sauvegarde localement dans ~/.openclaw/data/work-helper/ingest/.

    Returns:
        (email_subject, pdf_path) ou (error_message, None)
    """
    mail_script = _find_skill_script("mail-client", "mail.py")

    # chercher les emails recents avec PJ PDF
    try:
        result = subprocess.run(
            [sys.executable, str(mail_script),
             "search", "--query", "pdf",
             "--limit", "1"],
            capture_output=True, text=True, timeout=60,
        )
    except subprocess.TimeoutExpired:
        return "Timeout lors de la recherche email", None
    except FileNotFoundError:
        return "Python introuvable pour mail-client", None

    if result.returncode != 0:
        return f"Erreur mail-client search : {result.stderr.strip()}", None

    try:
        emails = json.loads(result.stdout)
    except json.JSONDecodeError:
        return "Reponse mail-client invalide (non-JSON)", None

    if not emails:
        return "Aucun email avec PJ PDF trouve", None

    email = emails[0] if isinstance(emails, list) else emails
    subject = email.get("subject", "(sans sujet)")
    msg_id = email.get("id") or email.get("uid")

    if not msg_id:
        return "Email trouve mais sans identifiant", None

    # lire le contenu complet de l'email (avec PJ base64)
    try:
        result = subprocess.run(
            [sys.executable, str(mail_script),
             "read", str(msg_id)],
            capture_output=True, text=True, timeout=120,
        )
    except subprocess.TimeoutExpired:
        return "Timeout lors de la lecture email", None

    if result.returncode != 0:
        return f"Erreur mail-client read : {result.stderr.strip()}", None

    try:
        msg_data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return "Reponse mail-client read invalide (non-JSON)", None

    # extraire les PJ PDF (base64)
    attachments = msg_data.get("attachments", [])
    pdf_attachment = None
    for att in attachments:
        filename = att.get("filename", "").lower()
        content_type = att.get("content_type", "").lower()
        if filename.endswith(".pdf") or "pdf" in content_type:
            pdf_attachment = att
            break

    if not pdf_attachment:
        return f"Email '{subject}' trouve mais sans PJ PDF", None

    # sauvegarder le PDF
    import base64

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    download_dir = _DATA_DIR / "ingest"
    download_dir.mkdir(exist_ok=True)

    pdf_filename = pdf_attachment.get("filename", "remarkable.pdf")
    # sanitize filename
    pdf_filename = "".join(
        c for c in pdf_filename if c.isalnum() or c in ".-_ "
    ).strip() or "remarkable.pdf"
    pdf_path = download_dir / pdf_filename

    try:
        pdf_data = base64.b64decode(pdf_attachment.get("data", ""))
        pdf_path.write_bytes(pdf_data)
    except Exception as exc:
        return f"Erreur decodage PJ : {exc}", None

    return subject, str(pdf_path)


def build_ingest_output(mode: str, llm_result: str, *,
                        project: str = "",
                        subject: str = "") -> dict:
    """Formate le resultat d'ingestion pour affichage/stockage.

    Returns:
        {mode, subject, project, content, entries (si log/cra)}
    """
    output = {
        "mode": mode,
        "subject": subject,
        "project": project,
        "content": llm_result,
    }

    # pour les modes log et cra, tenter de parser le JSON du LLM
    if mode in ("log", "cra"):
        try:
            # extraire le JSON du texte (le LLM peut wrapper dans du markdown)
            text = llm_result
            if "```json" in text:
                text = text.split("```json", 1)[1].split("```", 1)[0]
            elif "```" in text:
                text = text.split("```", 1)[1].split("```", 1)[0]
            entries = json.loads(text.strip())
            if isinstance(entries, list):
                output["entries"] = entries
        except (json.JSONDecodeError, IndexError):
            pass  # garder le texte brut

    return output


def auto_log_entries(entries: list, project: str = "") -> int:
    """Logue automatiquement les entrees extraites par ingestion.

    Importe _journal ici pour eviter les imports circulaires.
    Returns: nombre d'entrees ajoutees.
    """
    from _journal import add as journal_add

    count = 0
    for e in entries:
        text = e.get("text", "")
        if not text:
            continue
        journal_add(
            text,
            project=e.get("project", project),
            duration=e.get("duration", ""),
            tags="ingest,remarkable",
        )
        count += 1
    return count


def auto_note_content(content: str, project: str = "") -> dict:
    """Stocke le resultat d'ingestion comme note.

    Importe _notes ici pour eviter les imports circulaires.
    Returns: la note creee.
    """
    from _notes import add as note_add

    return note_add(content, project=project)
