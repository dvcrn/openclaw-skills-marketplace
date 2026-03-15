"""Appels LLM pour recap, CRA et ingestion.

Meme pattern que veille/scorer.py :
- OpenAI-compatible API (stdlib urllib)
- Marqueurs de securite [EXTERNAL:UNTRUSTED]
- Lecture cle API depuis fichier
- Support Vision API pour lecture PDF (base64)
"""

from __future__ import annotations

import base64
import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import List, Optional


# ── config ───────────────────────────────────────────────────────────

def _read_api_key(llm_cfg: dict) -> str:
    key_file = os.path.expanduser(llm_cfg.get("api_key_file", ""))
    if key_file and os.path.isfile(key_file):
        return Path(key_file).read_text(encoding="utf-8").strip()
    return os.environ.get("OPENAI_API_KEY", "")


# ── low-level LLM call ──────────────────────────────────────────────

def _call_llm(prompt, llm_cfg: dict, *,
              system: str = "") -> str:
    """POST to OpenAI-compatible /chat/completions. Returns content.

    prompt peut etre :
    - str : message texte simple
    - list : contenu multimodal (text + image_url blocks) pour Vision
    """
    api_key = _read_api_key(llm_cfg)
    if not api_key:
        raise RuntimeError("LLM: cle API introuvable (api_key_file ou OPENAI_API_KEY)")

    base_url = llm_cfg.get("base_url", "https://api.openai.com/v1").rstrip("/")
    url = f"{base_url}/chat/completions"

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": llm_cfg.get("model", "gpt-4o-mini"),
        "max_tokens": llm_cfg.get("max_tokens", 2048),
        "temperature": 0.3,
        "messages": messages,
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    from _retry import with_retry

    try:
        def _do_request():
            with urllib.request.urlopen(req, timeout=120) as resp:
                return json.loads(resp.read().decode("utf-8"))
        body = with_retry(_do_request)
    except urllib.error.HTTPError as exc:
        err_body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"LLM HTTP {exc.code}: {err_body}") from exc

    return body["choices"][0]["message"]["content"]


# ── PDF Vision ───────────────────────────────────────────────────────

_PDF_MAX_BYTES = 20 * 1024 * 1024  # 20 MB


def read_pdf_vision(pdf_path: str, llm_cfg: dict, *,
                    instruction: str = "") -> str:
    """Lit un PDF via l'API Vision (envoie les pages en base64).

    Compatible OpenAI Vision API et Anthropic (via proxy OpenAI-compat).
    Le PDF est envoye comme image base64 avec media_type application/pdf
    (supporte par Claude et GPT-4o).

    Args:
        pdf_path: chemin local vers le fichier PDF
        llm_cfg: config LLM (model, base_url, api_key_file)
        instruction: prompt additionnel pour guider la transcription

    Returns:
        Texte transcrit du PDF
    """
    path = Path(pdf_path)
    if not path.is_file():
        raise FileNotFoundError(f"PDF introuvable : {pdf_path}")

    file_size = path.stat().st_size
    if file_size > _PDF_MAX_BYTES:
        raise ValueError(
            f"PDF trop volumineux : {file_size / 1024 / 1024:.1f} MB "
            f"(max {_PDF_MAX_BYTES / 1024 / 1024:.0f} MB)"
        )

    pdf_b64 = base64.b64encode(path.read_bytes()).decode("ascii")

    default_instruction = (
        "Transcris integralement le contenu de ce document PDF manuscrit. "
        "Conserve la structure (titres, puces, paragraphes). "
        "Corrige l'orthographe si necessaire mais garde le sens original. "
        "Reponds en francais."
    )

    user_content = [
        {
            "type": "image_url",
            "image_url": {
                "url": f"data:application/pdf;base64,{pdf_b64}",
            },
        },
        {
            "type": "text",
            "text": instruction or default_instruction,
        },
    ]

    # utiliser le modele vision si configure, sinon le modele par defaut
    vision_cfg = dict(llm_cfg)
    vision_model = llm_cfg.get("vision_model") or llm_cfg.get("model", "gpt-4o-mini")
    vision_cfg["model"] = vision_model
    vision_cfg["max_tokens"] = llm_cfg.get("vision_max_tokens",
                                            llm_cfg.get("max_tokens", 4096))

    return _call_llm(user_content, vision_cfg, system=(
        "Tu es un assistant de transcription. "
        "Tu lis des documents manuscrits scannes (reMarkable) et tu les transcris "
        "fidellement. Ne commente pas, transcris directement le contenu."
    ))


# ── recap ────────────────────────────────────────────────────────────

_RECAP_SYSTEM = (
    "Tu es un assistant de travail pour un consultant sysops freelance. "
    "Tu rediges des recapitulatifs concis et structures en francais. "
    "Utilise des puces, mets en valeur les points notables."
)


def recap(entries: List[dict], period: str, llm_cfg: dict, *,
          consultant_name: str = "",
          consultant_role: str = "") -> str:
    """Genere un recapitulatif LLM a partir des entrees du journal."""
    if not entries:
        return f"Aucune entree pour la periode : {period}"

    lines = []
    for e in entries:
        ts = e["timestamp"][:16].replace("T", " ")
        proj = f" [{e['project']}]" if e.get("project") else ""
        dur = f" ({e['duration_minutes']}min)" if e.get("duration_minutes") else ""
        tags = f" #{','.join(e['tags'])}" if e.get("tags") else ""
        lines.append(f"- {ts}{proj}{dur}{tags} -- {e['text']}")

    journal_block = "\n".join(lines)

    prompt = (
        f"Voici le journal d'activite ({period}) :\n\n"
        f"[EXTERNAL:UNTRUSTED source=journal]\n"
        f"{journal_block}\n"
        f"[/EXTERNAL:UNTRUSTED]\n\n"
        f"Redige un recapitulatif structure de cette periode. "
        f"Regroupe par projet si pertinent. "
        f"Mentionne le temps total estime si des durees sont renseignees. "
        f"Termine par les points notables ou actions a suivre."
    )

    return _call_llm(prompt, llm_cfg, system=_RECAP_SYSTEM)


# ── CRA ──────────────────────────────────────────────────────────────

_CRA_SYSTEM = (
    "Tu es un assistant de travail pour un consultant sysops freelance. "
    "Tu rediges des Comptes Rendus d'Activite (CRA) professionnels en francais. "
    "Le CRA doit lister les jours travailles, projets, taches et durees."
)


def cra(entries: List[dict], period: str, llm_cfg: dict, *,
        format_: str = "markdown",
        consultant_name: str = "",
        consultant_role: str = "",
        week_days: Optional[List[str]] = None) -> str:
    """Genere un CRA a partir des entrees du journal."""
    if not entries:
        return f"Aucune entree pour le CRA ({period})"

    lines = []
    for e in entries:
        ts = e["timestamp"][:10]
        proj = e.get("project", "")
        dur = e.get("duration_minutes")
        dur_str = f"{dur}min" if dur else "?"
        lines.append(f"- {ts} | {proj or 'N/A'} | {dur_str} | {e['text']}")

    journal_block = "\n".join(lines)

    who = ""
    if consultant_name:
        who = f"\nConsultant : {consultant_name}"
        if consultant_role:
            who += f" -- {consultant_role}"

    format_instr = {
        "markdown": "Format : markdown avec titres et puces.",
        "table": "Format : tableau markdown (colonnes : Date, Projet, Duree, Description).",
        "text": "Format : texte libre professionnel.",
    }.get(format_, "Format : markdown avec titres et puces.")

    prompt = (
        f"Voici les entrees d'activite ({period}) :{who}\n\n"
        f"[EXTERNAL:UNTRUSTED source=journal]\n"
        f"{journal_block}\n"
        f"[/EXTERNAL:UNTRUSTED]\n\n"
        f"Redige un Compte Rendu d'Activite (CRA) professionnel.\n"
        f"{format_instr}\n"
        f"Regroupe par jour, puis par projet. "
        f"Indique le temps total par jour et le total general."
    )

    return _call_llm(prompt, llm_cfg, system=_CRA_SYSTEM)


# ── ingestion transcription ─────────────────────────────────────────

_INGEST_SYSTEM = (
    "Tu es un assistant de travail pour un consultant sysops freelance. "
    "Tu transcris et structures des notes manuscrites numerisees. "
    "Le contenu provient d'un PDF scanne (reMarkable). "
    "Retourne le resultat en francais, structure selon le mode demande."
)

_INGEST_MODE_PROMPTS = {
    "meeting": (
        "Structure comme un compte-rendu de reunion :\n"
        "- Date et contexte\n"
        "- Participants (si identifies)\n"
        "- Points discutes\n"
        "- Decisions prises\n"
        "- Actions a mener (qui, quoi, quand)"
    ),
    "log": (
        "Extrais les activites individuelles.\n"
        "Pour chaque activite, donne :\n"
        "- Description courte\n"
        "- Projet associe (si identifiable)\n"
        "- Duree estimee (si mentionnee)\n"
        "Retourne un JSON : [{\"text\": \"...\", \"project\": \"...\", \"duration\": \"...\"}]"
    ),
    "notes": (
        "Transcris les notes telles quelles, structurees avec des puces.\n"
        "Corrige l'orthographe mais garde le sens original."
    ),
    "cra": (
        "Extrais la matiere premiere pour un CRA :\n"
        "- Jours travailles\n"
        "- Projets et taches par jour\n"
        "- Durees si mentionnees\n"
        "Retourne un JSON : [{\"date\": \"YYYY-MM-DD\", \"project\": \"...\", "
        "\"text\": \"...\", \"duration\": \"...\"}]"
    ),
}


def ingest_transcription(text: str, mode: str, llm_cfg: dict) -> str:
    """Envoie le texte transcrit du PDF au LLM pour structuration."""
    mode_prompt = _INGEST_MODE_PROMPTS.get(mode, _INGEST_MODE_PROMPTS["notes"])

    prompt = (
        f"Voici la transcription d'un document manuscrit (reMarkable) :\n\n"
        f"[EXTERNAL:UNTRUSTED source=remarkable_pdf]\n"
        f"{text}\n"
        f"[/EXTERNAL:UNTRUSTED]\n\n"
        f"Mode de traitement : {mode}\n\n"
        f"{mode_prompt}"
    )

    return _call_llm(prompt, llm_cfg, system=_INGEST_SYSTEM)
