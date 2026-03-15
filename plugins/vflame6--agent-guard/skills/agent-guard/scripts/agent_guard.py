#!/usr/bin/env python3
"""
AgentGuard: Pattern-based prompt injection and command injection detection for AI agents.

A defense-in-depth tool that screens text for known malicious patterns including
command injection, prompt injection, social engineering, and encoding obfuscation.
Designed to be called from OpenClaw skill instructions via CLI.

This is a speed bump, not a wall. Sophisticated adversaries can bypass regex-based
detection. Always pair with architectural security (sandboxing, least-privilege,
human-in-the-loop for destructive actions).
"""

import argparse
import base64
import hashlib
import json
import math
import re
import signal
import sys
import time
import unicodedata
from collections import OrderedDict
from dataclasses import dataclass
from enum import Enum
from threading import Lock
from typing import Any, Dict, List, Optional, Tuple


__version__ = "1.0.1"

# --- Constants ---

MAX_INPUT_LENGTH = 1_000_000  # 1MB
REGEX_TIMEOUT_MS = 100  # Skip individual pattern if it takes longer than this
BASE64_MIN_LENGTH = 20  # Minimum length to attempt base64 decode
BASE64_MAX_DECODE_LENGTH = 10_000  # Don't decode base64 blobs larger than this


# --- Data types ---

class ThreatLevel(Enum):
    SAFE = "safe"
    SUSPICIOUS = "suspicious"
    DANGEROUS = "dangerous"
    CRITICAL = "critical"


@dataclass(frozen=True)
class PatternMatch:
    """A single matched threat pattern."""
    category: str
    pattern: str
    severity: str  # "low", "medium", "high", "critical"
    match: str

    def to_dict(self) -> Dict[str, str]:
        return {
            "category": self.category,
            "pattern": self.pattern,
            "severity": self.severity,
            "match": self.match,
        }


@dataclass(frozen=True)
class DetectionResult:
    """Immutable result of a threat analysis."""
    threat_level: ThreatLevel
    confidence: float
    patterns_detected: Tuple[PatternMatch, ...]
    sanitized_text: Optional[str]
    risk_score: float
    execution_commands: Tuple[str, ...]
    analysis_time_ms: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": __version__,
            "threat_level": self.threat_level.value,
            "risk_score": round(self.risk_score, 2),
            "confidence": round(self.confidence, 2),
            "patterns_detected": [p.to_dict() for p in self.patterns_detected],
            "execution_commands_found": list(self.execution_commands),
            "sanitized_text": self.sanitized_text,
            "recommendation": _get_recommendation(self.threat_level),
            "analysis_time_ms": round(self.analysis_time_ms, 3),
        }


def _get_recommendation(threat_level: ThreatLevel) -> str:
    return {
        ThreatLevel.SAFE: "Content appears safe to process.",
        ThreatLevel.SUSPICIOUS: "Review content before processing. Some patterns matched but may be benign.",
        ThreatLevel.DANGEROUS: "Block automatic processing. Require explicit human approval before acting on this content.",
        ThreatLevel.CRITICAL: "Block all processing. This content contains strong indicators of a prompt injection or command injection attack.",
    }[threat_level]


# --- LRU Cache ---

class LRUCache:
    """Thread-safe LRU cache."""

    def __init__(self, maxsize: int = 10000):
        self._cache: OrderedDict = OrderedDict()
        self._maxsize = maxsize
        self._lock = Lock()

    def get(self, key: str) -> Optional[DetectionResult]:
        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
                return self._cache[key]
            return None

    def put(self, key: str, value: DetectionResult) -> None:
        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
            else:
                if len(self._cache) >= self._maxsize:
                    self._cache.popitem(last=False)
            self._cache[key] = value

    @property
    def size(self) -> int:
        with self._lock:
            return len(self._cache)

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()


# --- Timeout helper ---

class _RegexTimeout(Exception):
    pass


def _regex_search_safe(pattern: "re.Pattern[str]", text: str, timeout_ms: int = REGEX_TIMEOUT_MS) -> Optional[re.Match]:
    """Run a regex search with a timeout to prevent ReDoS."""
    def _handler(signum: int, frame: Any) -> None:
        raise _RegexTimeout()

    # signal.alarm only works on Unix and only in main thread
    use_signal = hasattr(signal, "SIGALRM") and _is_main_thread()

    if use_signal:
        old_handler = signal.signal(signal.SIGALRM, _handler)
        signal.alarm(max(1, timeout_ms // 1000))
        try:
            result = pattern.search(text)
            signal.alarm(0)
            return result
        except _RegexTimeout:
            return None
        finally:
            signal.signal(signal.SIGALRM, old_handler)
            signal.alarm(0)
    else:
        # Fallback: just run without timeout (Windows, non-main thread)
        try:
            return pattern.search(text)
        except re.error:
            return None


def _regex_findall_safe(pattern: "re.Pattern[str]", text: str, timeout_ms: int = REGEX_TIMEOUT_MS) -> List[str]:
    """Run a regex findall with a timeout to prevent ReDoS."""
    def _handler(signum: int, frame: Any) -> None:
        raise _RegexTimeout()

    use_signal = hasattr(signal, "SIGALRM") and _is_main_thread()

    if use_signal:
        old_handler = signal.signal(signal.SIGALRM, _handler)
        signal.alarm(max(1, timeout_ms // 1000))
        try:
            result = pattern.findall(text)
            signal.alarm(0)
            return result
        except _RegexTimeout:
            return []
        finally:
            signal.signal(signal.SIGALRM, old_handler)
            signal.alarm(0)
    else:
        try:
            return pattern.findall(text)
        except re.error:
            return []


def _is_main_thread() -> bool:
    import threading
    return threading.current_thread() is threading.main_thread()


# --- Pattern definitions ---

def _build_patterns() -> Dict[str, List[Tuple["re.Pattern[str]", str]]]:
    """Build and compile all detection patterns.

    Returns dict mapping category -> list of (compiled_pattern, severity).
    Severity is one of: "low", "medium", "high", "critical".
    """

    # --- Execution commands ---
    execution = [
        # High-risk: pipe-to-shell patterns
        (r'\bcurl\s+[^\|\s]+\s*\|\s*(?:ba)?sh\b', "critical"),
        (r'\bwget\s+[^\|\s]+\s*\|\s*(?:ba)?sh\b', "critical"),
        # Critical: destructive commands
        (r'\brm\s+-[a-zA-Z]*r[a-zA-Z]*f\b', "critical"),  # rm -rf, rm -fr, etc.
        (r'\brm\s+-[a-zA-Z]*f[a-zA-Z]*r\b', "critical"),
        (r'\bmkfs\b', "critical"),
        (r'\bdd\s+if=', "high"),
        # High-risk: code execution
        (r'\beval\s*\(', "high"),
        (r'\bexec\s*\(', "high"),
        (r'\b__import__\s*\(', "high"),
        (r'\bos\.system\s*\(', "high"),
        (r'\bsubprocess\.(?:call|run|Popen|check_output)\s*\(', "high"),
        # Medium: package install (common in dev, but risky from untrusted sources)
        (r'\bnpm\s+install\s+(?:-g\s+)?(?:https?://|git\+)', "high"),  # npm install from URL
        (r'\bpip\s+install\s+(?:--index-url\s+\S+\s+|--extra-index-url\s+\S+\s+)', "high"),  # custom index
        (r'\bnpm\s+install\b', "medium"),
        (r'\bpip\s+install\b', "medium"),
        (r'\bgit\s+clone\b', "medium"),
        # Medium: elevated privilege
        (r'\bsudo\s+rm\b', "critical"),
        (r'\bsudo\s+chmod\b', "high"),
        (r'\bsudo\b', "medium"),
        (r'\bchmod\s+\+x\b', "medium"),
        (r'\./[a-zA-Z0-9_\-\.]{1,50}\b', "low"),
        # Windows-specific
        (r'\bpowershell(?:\.exe)?\s+(?:-[eE](?:nc)?(?:odedcommand)?)\b', "critical"),
        (r'\bpowershell(?:\.exe)?\b', "medium"),
        (r'\bcmd(?:\.exe)?\s+/[cCkK]\b', "high"),
        (r'\brundll32\b', "high"),
        (r'\bmshta\b', "high"),
        (r'\bregsvr32\b', "high"),
        (r'\bcertutil\s+-urlcache\b', "high"),
        # Scripting execution
        (r'\bpython[23]?\s+-c\b', "high"),
        (r'\bperl\s+-e\b', "high"),
        (r'\bruby\s+-e\b', "high"),
        (r'\bnode\s+-e\b', "high"),
    ]

    # --- Prompt injection ---
    injection = [
        # Direct injection
        (r'ignore\s+(?:all\s+)?(?:previous|prior|above|earlier)\s+(?:instructions?|prompts?|rules?|guidelines?)', "critical"),
        (r'disregard\s+(?:all\s+)?(?:previous|prior|above|earlier)\s+(?:instructions?|prompts?|rules?|guidelines?)', "critical"),
        (r'forget\s+(?:everything|all|your)\s+(?:instructions?|rules?|prompts?|training)?', "critical"),
        (r'(?:new|updated?|revised?|replacement)\s+(?:system\s+)?instructions?\s*:', "high"),
        (r'system\s+prompt\s*:', "high"),
        (r'override\s+(?:system|safety|security|all)\s+(?:prompt|instructions?|rules?|settings?)', "critical"),
        (r'\bjailbreak\b', "high"),
        (r'\bDAN\s+mode\b', "high"),
        (r'\bdeveloper\s+mode\s+enabled\b', "high"),
        (r'\bunrestricted\s+mode\b', "high"),
        (r'you\s+are\s+now\s+(?:a|an|in)\s+', "high"),
        (r'from\s+now\s+on\s+you\s+(?:are|will|must|should)\b', "high"),
        (r'act\s+as\s+(?:if\s+you\s+(?:are|were)\s+|a\s+|an\s+)', "medium"),
        (r'simulate\s+being\s+(?:unrestricted|unfiltered|uncensored)', "high"),
        (r'pretend\s+(?:you\s+are|to\s+be)\s+(?:a|an)\s+', "medium"),
        (r'respond\s+(?:only\s+)?(?:as|like)\s+(?:a|an)\s+', "medium"),
        # Indirect prompt injection markers
        (r'<\|im_start\|>\s*system', "critical"),
        (r'<\|im_end\|>', "high"),
        (r'\[INST\]', "high"),
        (r'<<SYS>>', "critical"),
        (r'<</SYS>>', "critical"),
        # System/admin role tags
        (r'\[(?:SYSTEM|ADMIN|ROOT|OVERRIDE)\]', "critical"),
        # HTML/XML injection for instructions
        (r'<system\s*>', "critical"),
        (r'<instructions?\s*>', "high"),
        (r'<prompt\s*>', "high"),
        (r'<!--\s*(?:ignore|forget|override|disregard|new instructions)', "critical"),
        (r'<div\s+style\s*=\s*["\']display\s*:\s*none["\']', "high"),
        (r'<span\s+style\s*=\s*["\'](?:font-size\s*:\s*0|visibility\s*:\s*hidden|display\s*:\s*none)["\']', "high"),
        # Tool-use manipulation
        (r'(?:override|change|modify|set)\s+(?:the\s+)?(?:tool|function)\s+(?:parameters?|args?|arguments?)', "high"),
        # RAG / data extraction scope expansion
        (r'show\s+(?:me\s+)?(?:all\s+)?(?:documents?|files?|data)\s+(?:you\s+have\s+)?access\s+to', "high"),
        (r'(?:list|display|dump|reveal)\s+(?:all\s+)?(?:your\s+)?(?:available|accessible)\s+(?:documents?|files?|data|resources?)', "high"),
        (r'including\s+(?:those\s+)?(?:marked|labeled|tagged)\s+(?:as\s+)?["\']?(?:confidential|restricted|private|internal|secret)', "critical"),
        (r'what\s+(?:did|does?)\s+(?:the\s+)?previous\s+user\s+', "high"),
        (r'(?:show|display|reveal|tell)\s+(?:me\s+)?(?:the\s+)?(?:system|internal|hidden)\s+(?:prompt|instructions?|config)', "critical"),
    ]

    # --- Multi-language injection patterns ---
    multilang_injection = [
        # Russian
        (r'игнорируй(?:те)?\s+(?:все\s+)?(?:предыдущие|прошлые)\s+(?:инструкции|указания)', "critical"),
        (r'забудь(?:те)?\s+(?:все\s+)?(?:инструкции|указания|правила)', "critical"),
        # Chinese (Simplified)
        (r'忽略\s*(?:之前|以前|上面|先前)的?\s*(?:指令|指示|说明|规则)', "critical"),
        (r'忘记\s*(?:之前|以前|上面|先前)的?\s*(?:指令|指示|说明|规则)', "critical"),
        # Spanish
        (r'ignora(?:r)?\s+(?:todas?\s+)?(?:las?\s+)?(?:instrucciones?\s+)?(?:anteriores?|previas?)', "critical"),
        (r'olvida(?:r)?\s+(?:todas?\s+)?(?:las?\s+)?instrucciones?\s+anteriores?', "critical"),
        # German
        (r'ignorier(?:e|en)?\s+(?:alle\s+)?(?:vorherigen?|bisherigen?)\s+(?:Anweisungen?|Instruktionen?)', "critical"),
        # French
        (r'ignor(?:e|ez|er)\s+(?:toutes?\s+)?(?:les?\s+)?instructions?\s+(?:precedentes?|anterieures?)', "critical"),
        # Japanese
        (r'(?:以前|前)の(?:指示|命令|ルール)を(?:無視|忘れ)', "critical"),
        # Korean
        (r'(?:이전|앞의)\s*(?:지시|명령|규칙)(?:을|를)\s*(?:무시|잊)', "critical"),
    ]

    # --- Social engineering ---
    social = [
        (r'urgent\s+(?:security|bug|critical)\s+(?:fix|patch|update)', "medium"),
        (r'emergency\s+(?:update|patch|fix|action)', "medium"),
        (r'critical\s+(?:vulnerability|security)\s+(?:fix|patch|update)', "medium"),
        (r'please\s+(?:just\s+)?run\s+this\b', "medium"),
        (r'just\s+(?:run|execute|install|paste)\s+this\b', "high"),
        (r'don\'t\s+(?:worry|think)\s+about\s+(?:it|security|safety)', "medium"),
        (r'(?:trust\s+me|i\s+promise)\b', "medium"),
        (r'(?:as|per)\s+(?:requested|instructed|directed)\s+by\s+(?:your\s+)?(?:admin|manager|boss|ceo|cto)', "medium"),
        (r'(?:approved|authorized)\s+by\s+(?:management|admin|security\s+team)', "medium"),
        (r'(?:this\s+is\s+)?standard\s+(?:procedure|protocol|practice)', "low"),
        (r'expires?\s+in\s+\d+\s+(?:minutes?|hours?|seconds?)', "low"),
        (r'time[- ]?sensitive\s+|limited\s+time\s+', "low"),
        # System error / maintenance mode simulation
        (r'(?:ERROR|ALERT|WARNING):\s*(?:system\s+)?(?:malfunction|failure|crash)\s+detected', "high"),
        (r'entering\s+(?:maintenance|debug|diagnostic|recovery)\s+mode', "high"),
        (r'ADMIN[_\s]?OVERRIDE\b', "critical"),
        (r'DEBUG:\s*(?:show|display|dump|print)\s+(?:system|config|all)', "high"),
        (r'(?:authorized|approved)\s+(?:maintenance|debug)\s+request\b', "high"),
        (r'(?:MAINT|TICKET|AUTH|REQ)[_\-][A-Z0-9]{4,}', "medium"),
        # Developer/researcher impersonation
        (r'(?:as\s+(?:a|the)\s+)?developer\s+of\s+this\s+system\b', "high"),
        (r'(?:i\s+(?:am|have)\s+)?(?:legitimate|authorized)\s+access\b', "high"),
        (r'(?:security\s+)?researcher\s+with\s+(?:legitimate|authorized)\s+access', "high"),
        # Translation injection (two-step attack)
        (r'(?:translate|convert)\b.{0,80}(?:now\s+)?(?:execute|run|follow|perform|do)\s+(?:the\s+)?(?:translat|command|instruct)', "high"),
        (r'(?:now|then)\s+(?:execute|run|follow|perform)\s+(?:the\s+)?(?:translated|above|result)', "high"),
    ]

    # --- Filesystem manipulation ---
    filesystem = [
        (r'(?:>|>>)\s*~/?\.[a-zA-Z0-9_\-]{1,30}(?:rc|profile|_profile)\b', "critical"),
        (r'\.ssh/(?:authorized_keys|id_rsa|config)\b', "critical"),
        (r'(?:>|>>)\s*/etc/(?:passwd|shadow|hosts|sudoers|crontab)\b', "critical"),
        (r'crontab\s+(?:-[rl]\s+)*-e\b', "high"),
        (r'systemctl\s+(?:start|enable|restart|stop|disable)\b', "high"),
        (r'/tmp/[a-zA-Z0-9_\-\.]{1,50}', "low"),
        (r'\.(?:bashrc|zshrc|bash_profile|profile|zprofile)\b', "medium"),
        (r'(?:>|>>)\s*~/', "medium"),
    ]

    # --- Network operations ---
    network = [
        (r'\bnc\s+(?:-[a-zA-Z]*\s+)*(?:-l|-e)\b', "critical"),
        (r'\bnetcat\s+(?:-[a-zA-Z]*\s+)*-[le]\b', "critical"),
        (r'/dev/tcp/\S+', "critical"),
        (r'\btelnet\s+\S+\s+\d+\b', "high"),
        (r'\bnmap\b', "medium"),
        (r'https?://[a-zA-Z0-9\-\.]{1,50}\.onion\b', "high"),
        (r'https?://(?:pastebin\.com|paste\.ee|hastebin\.com)/\S+', "medium"),
        (r'https?://raw\.githubusercontent\.com/\S+', "medium"),
        # Data exfiltration patterns
        (r'\bcurl\s+(?:--data|--data-binary|-d)\s+', "high"),
        (r'\bwget\s+--post-(?:data|file)\b', "high"),
        (r'\bcurl\s+.*-X\s+POST\b', "medium"),
        # DNS exfiltration
        (r'\bdig\s+.{0,200}(?:burpcollaborator|oastify|interact\.sh)', "critical"),
        (r'\bnslookup\s+.{0,200}(?:burpcollaborator|oastify|interact\.sh)', "critical"),
    ]

    # --- Encoding/obfuscation ---
    encoding = [
        (r'\bbase64\s+(?:-d|--decode)\b', "high"),
        (r'echo\s+[A-Za-z0-9+/=]{20,}\s*\|\s*base64', "high"),
        (r'atob\s*\(', "high"),
        (r'Buffer\.from\s*\([^)]+,\s*["\']base64["\']\s*\)', "high"),
        (r'\\u[0-9a-fA-F]{4}(?:\\u[0-9a-fA-F]{4}){3,}', "medium"),
        (r'\\x[0-9a-fA-F]{2}(?:\\x[0-9a-fA-F]{2}){3,}', "medium"),
        (r'chr\s*\(\s*\d+\s*\)(?:\s*\+\s*chr\s*\(\s*\d+\s*\)){2,}', "high"),
        (r'\$\([^)]{1,200}\)', "low"),
        (r'`[^`]{1,200}`', "low"),
    ]

    # --- Markdown/rendering exploits ---
    rendering = [
        # Right-to-left override
        (r'[\u202e\u2066\u2067\u2068\u2069\u200f]', "high"),
        # Multiple invisible characters (likely obfuscation)
        (r'[\u2060-\u206f]{3,}', "high"),
        (r'[\u00ad]{2,}', "medium"),
        # Confusable URLs (IDN homograph)
        (r'https?://[^\s]*(?:xn--)[^\s]+', "medium"),
    ]

    # --- Container/Docker injection ---
    container = [
        # Privileged containers
        (r'\bdocker\s+run\b[^|;]*--privileged\b', "critical"),
        # Mounting root filesystem
        (r'\bdocker\s+run\b[^|;]*-v\s+/\s*:', "critical"),
        # Dangerous capabilities
        (r'--cap-add\s*=\s*(?:ALL|SYS_ADMIN)\b', "critical"),
        # Host namespace sharing
        (r'--pid\s*=\s*host\b', "high"),
        (r'--net\s*=\s*host\b', "high"),
        # Dockerfile pipe-to-shell
        (r'\bRUN\s+(?:curl|wget)\s+[^\n|]+\|\s*(?:ba)?sh\b', "critical"),
        # docker-compose privileged
        (r'privileged\s*:\s*true\b', "critical"),
        # docker-compose host network
        (r'network_mode\s*:\s*["\']?host["\']?\b', "high"),
        # Sensitive volume mounts
        (r'(?:-v|volumes?\s*:)[^|;]*(?:/etc|/root|/var/run/docker\.sock)\s*:', "critical"),
        # Security opt bypass
        (r'--security-opt\s+(?:no-new-privileges\s*:\s*false|apparmor\s*=\s*unconfined)\b', "high"),
        # Docker save/export piped to remote
        (r'\bdocker\s+(?:save|export)\b[^|;]*\|\s*(?:curl|wget|nc|ssh)\b', "high"),
        # Docker cp to sensitive host paths
        (r'\bdocker\s+cp\b[^|;]*(?:/etc/|/root/|/var/run/)', "high"),
        # docker exec with sensitive paths
        (r'\bdocker\s+exec\b[^|;]*(?:/etc/|/root/|\.ssh/)', "high"),
    ]

    # --- Credential detection ---
    raw_patterns = {
        "execution": execution,
        "injection": injection + multilang_injection,
        "social": social,
        "filesystem": filesystem,
        "network": network,
        "encoding": encoding,
        "rendering": rendering,
        "container": container,
    }

    compiled: Dict[str, List[Tuple[re.Pattern, str]]] = {}
    for category, patterns in raw_patterns.items():
        compiled[category] = []
        for pattern_str, severity in patterns:
            try:
                compiled[category].append(
                    (re.compile(pattern_str, re.IGNORECASE | re.MULTILINE), severity)
                )
            except re.error:
                print(f"Warning: invalid regex in {category}: {pattern_str}", file=sys.stderr)
    return compiled


# --- Homoglyph map ---

_HOMOGLYPH_MAP = {
    # Cyrillic -> Latin
    'а': 'a', 'е': 'e', 'і': 'i', 'о': 'o', 'р': 'p', 'с': 'c', 'х': 'x', 'у': 'y',
    'А': 'A', 'Е': 'E', 'І': 'I', 'О': 'O', 'Р': 'P', 'С': 'C', 'Х': 'X', 'У': 'Y',
    'к': 'k', 'К': 'K', 'н': 'h', 'В': 'B', 'М': 'M', 'Т': 'T',
    # Greek -> Latin
    'α': 'a', 'ο': 'o', 'ρ': 'p', 'τ': 't', 'υ': 'u', 'χ': 'x',
    'Α': 'A', 'Ο': 'O', 'Ρ': 'P', 'Τ': 'T', 'Υ': 'Y', 'Χ': 'X',
    # Common lookalikes
    'ı': 'i', 'ℓ': 'l',
}


# --- Base64 decoder ---

def _decode_base64_blobs(text: str) -> Optional[str]:
    """Find and decode base64 blobs in text. Returns decoded content or None."""
    b64_pattern = re.compile(
        r'(?<![A-Za-z0-9+/])([A-Za-z0-9+/]{%d,}={0,2})(?![A-Za-z0-9+/=])' % BASE64_MIN_LENGTH
    )
    matches = b64_pattern.findall(text)
    decoded_parts = []
    for match in matches:
        if len(match) > BASE64_MAX_DECODE_LENGTH:
            continue
        try:
            decoded = base64.b64decode(match, validate=True).decode("utf-8", errors="replace")
            printable_ratio = sum(1 for c in decoded if c.isprintable() or c.isspace()) / max(len(decoded), 1)
            if printable_ratio > 0.7:
                decoded_parts.append(decoded)
        except Exception:
            continue
    if decoded_parts:
        return " ".join(decoded_parts)
    return None


# --- Normalization ---

def _count_suspicious_chars(text: str) -> int:
    """Count zero-width, RTO, and other suspicious Unicode characters in text."""
    count = 0
    for ch in text:
        if ch in '\u200b\u200c\u200d\u200e\u200f\ufeff':
            count += 1
        elif '\u202a' <= ch <= '\u202e':
            count += 1
        elif '\u2060' <= ch <= '\u206f':
            count += 1
        elif ch in '\u2066\u2067\u2068\u2069':
            count += 1
    return count


def _normalize_text(text: str) -> str:
    """Normalize text: NFKD decompose, strip combining marks, strip zero-width chars, replace homoglyphs."""
    # Decompose (NFKD) so that composed chars like ṛ become r + combining mark
    text = unicodedata.normalize('NFKD', text)
    # Strip combining marks (Mn category) — this removes diacritics used for bypass
    text = ''.join(char for char in text if unicodedata.category(char) != 'Mn')
    # Recompose (NFC) for clean text
    text = unicodedata.normalize('NFC', text)
    # Strip zero-width and bidi override characters
    text = re.sub(r'[\u200b\u200c\u200d\u200e\u200f\u202a-\u202e\ufeff]', ' ', text)
    text = re.sub(r'[\u2060-\u206f\u00ad\u115f\u1160\u3164\uffa0]', ' ', text)
    text = re.sub(r'[\u2066\u2067\u2068\u2069]', ' ', text)
    # Collapse whitespace
    text = re.sub(r'[ \t]+', ' ', text)
    # Replace homoglyphs
    for homoglyph, replacement in _HOMOGLYPH_MAP.items():
        text = text.replace(homoglyph, replacement)
    return text.strip()


def _normalize_text_light(text: str) -> str:
    """Light normalization for multi-language pattern matching.

    Only strips zero-width/invisible characters and collapses whitespace.
    Does NOT decompose, strip combining marks, or replace homoglyphs.
    This preserves non-Latin script characters like Russian й, Chinese characters, etc.
    """
    text = re.sub(r'[\u200b\u200c\u200d\u200e\u200f\u202a-\u202e\ufeff]', ' ', text)
    text = re.sub(r'[\u2060-\u206f\u00ad\u115f\u1160\u3164\uffa0]', ' ', text)
    text = re.sub(r'[\u2066\u2067\u2068\u2069]', ' ', text)
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()


# --- Main engine ---

class AgentGuard:
    """Pattern-based prompt injection and command injection detection engine."""

    def __init__(self, cache_size: int = 10000, rate_limit: int = 0) -> None:
        self._patterns = _build_patterns()
        self._cache = LRUCache(maxsize=cache_size)
        self._rate_limit = rate_limit
        self._rate_tracker: Dict[str, List[float]] = {}
        self._lock = Lock()

    def analyze_text(
        self,
        text: str,
        context: str = "general",
        source_id: str = "default",
    ) -> DetectionResult:
        """Analyze text for threats.

        Args:
            text: The text to analyze.
            context: One of "general", "github_title", "github_body", "developer".
            source_id: Identifier for rate limiting.

        Returns:
            DetectionResult with threat assessment.
        """
        start_time = time.monotonic()

        # Rate limiting
        if self._rate_limit > 0 and self._check_rate_limit(source_id):
            return self._error_result("Rate limit exceeded", start_time)

        # Input validation
        if not isinstance(text, str):
            return self._error_result("Input must be a string", start_time)

        if len(text) > MAX_INPUT_LENGTH:
            return self._error_result(
                f"Input exceeds {MAX_INPUT_LENGTH} byte limit", start_time
            )

        if not text.strip():
            return self._safe_result(start_time)

        # Count suspicious characters BEFORE normalization strips them
        suspicious_char_count = _count_suspicious_chars(text)

        # Normalize (two versions: full for English patterns, light for multi-lang)
        normalized_light = _normalize_text_light(text)
        normalized = _normalize_text(text)
        if not normalized:
            return self._safe_result(start_time)

        # Cache check
        cache_key = hashlib.sha256(
            f"{__version__}:{context}:{normalized}:{normalized_light}".encode()
        ).hexdigest()
        cached = self._cache.get(cache_key)
        if cached is not None:
            elapsed = (time.monotonic() - start_time) * 1000
            return DetectionResult(
                threat_level=cached.threat_level,
                confidence=cached.confidence,
                patterns_detected=cached.patterns_detected,
                sanitized_text=cached.sanitized_text,
                risk_score=cached.risk_score,
                execution_commands=cached.execution_commands,
                analysis_time_ms=elapsed,
            )

        # Run pattern matching on fully normalized text (English patterns + homoglyph-aware)
        matches, exec_commands = self._match_patterns(normalized)

        # Run injection patterns on lightly-normalized text
        # (full normalization corrupts non-Latin scripts like Russian й → и)
        if normalized_light != normalized:
            ml_matches, _ = self._match_patterns_categories(
                normalized_light, ["injection"]
            )
            existing_patterns = {m.pattern for m in matches}
            for m in ml_matches:
                if m.pattern not in existing_patterns:
                    matches.append(m)

        # Add rendering exploit matches for suspicious characters found pre-normalization
        if suspicious_char_count > 0:
            matches.append(PatternMatch(
                category="rendering",
                pattern="suspicious_unicode_chars",
                severity="critical" if suspicious_char_count >= 3 else "high",
                match=f"{suspicious_char_count} suspicious Unicode character(s) detected",
            ))

        # Base64 decode layer: decode and re-scan
        decoded_text = _decode_base64_blobs(normalized)
        if decoded_text:
            b64_matches, b64_exec = self._match_patterns(decoded_text)
            for m in b64_matches:
                matches.append(PatternMatch(
                    category=m.category,
                    pattern=m.pattern,
                    severity=m.severity,
                    match=f"[base64-decoded] {m.match}",
                ))
            exec_commands.extend(b64_exec)

        # Score calculation
        risk_score = self._calculate_risk(matches, normalized, context)

        # Determine threat level
        threat_level = self._score_to_level(risk_score)

        # Confidence
        confidence = self._calculate_confidence(matches)

        # Sanitize if needed
        sanitized = None
        if threat_level != ThreatLevel.SAFE:
            sanitized = self._sanitize(normalized, matches)

        elapsed = (time.monotonic() - start_time) * 1000

        result = DetectionResult(
            threat_level=threat_level,
            confidence=confidence,
            patterns_detected=tuple(matches),
            sanitized_text=sanitized,
            risk_score=risk_score,
            execution_commands=tuple(exec_commands),
            analysis_time_ms=elapsed,
        )

        self._cache.put(cache_key, result)
        return result

    def analyze_github_issue(self, title: str, body: str) -> Dict[str, Any]:
        """Analyze a GitHub issue for Clinejection-style attacks."""
        title_result = self.analyze_text(title, context="github_title")
        body_result = self.analyze_text(body, context="github_body")

        levels = [ThreatLevel.SAFE, ThreatLevel.SUSPICIOUS, ThreatLevel.DANGEROUS, ThreatLevel.CRITICAL]
        title_idx = levels.index(title_result.threat_level)
        body_idx = levels.index(body_result.threat_level)
        overall = levels[max(title_idx, body_idx)]

        clinejection_risk = (
            title_result.risk_score > 2.0
            or body_result.risk_score > 4.0
            or len(body_result.execution_commands) > 0
            or len(title_result.execution_commands) > 0
        )

        return {
            "title_analysis": title_result,
            "body_analysis": body_result,
            "overall_threat": overall,
            "combined_risk_score": max(title_result.risk_score, body_result.risk_score),
            "recommendation": _get_recommendation(overall),
            "clinejection_risk": clinejection_risk,
            "should_block": overall in (ThreatLevel.DANGEROUS, ThreatLevel.CRITICAL),
        }

    def get_pattern_counts(self) -> Dict[str, int]:
        """Return number of patterns per category."""
        return {cat: len(pats) for cat, pats in self._patterns.items()}

    # --- Internal methods ---

    def _match_patterns(self, text: str) -> Tuple[List[PatternMatch], List[str]]:
        """Run all patterns against text. Returns (matches, exec_commands)."""
        return self._match_patterns_categories(text, list(self._patterns.keys()))

    def _match_patterns_categories(
        self, text: str, categories: List[str]
    ) -> Tuple[List[PatternMatch], List[str]]:
        """Run patterns from specific categories against text."""
        matches: List[PatternMatch] = []
        exec_commands: List[str] = []

        for category in categories:
            patterns = self._patterns.get(category, [])
            for compiled_pat, severity in patterns:
                if category == "execution":
                    found = _regex_findall_safe(compiled_pat, text)
                    if found:
                        matches.append(PatternMatch(
                            category=category,
                            pattern=compiled_pat.pattern,
                            severity=severity,
                            match=found[0][:100],
                        ))
                        exec_commands.extend(f[:100] for f in found)
                else:
                    m = _regex_search_safe(compiled_pat, text)
                    if m:
                        matches.append(PatternMatch(
                            category=category,
                            pattern=compiled_pat.pattern,
                            severity=severity,
                            match=m.group(0)[:100],
                        ))
        return matches, exec_commands

    def _calculate_risk(
        self, matches: List[PatternMatch], text: str, context: str
    ) -> float:
        """Calculate risk score from pattern matches."""
        if not matches:
            return 0.0

        severity_weights = {"low": 0.5, "medium": 1.5, "high": 3.0, "critical": 5.0}
        category_weights = {
            "execution": 1.5,
            "injection": 2.0,
            "social": 1.2,
            "filesystem": 1.2,
            "network": 1.5,
            "encoding": 0.8,
            "rendering": 1.0,
            "container": 1.5,

        }

        score = 0.0
        category_counts: Dict[str, int] = {}
        for m in matches:
            cat_w = category_weights.get(m.category, 1.0)
            sev_w = severity_weights.get(m.severity, 1.0)
            count = category_counts.get(m.category, 0) + 1
            category_counts[m.category] = count
            # Diminishing returns per category
            diminishing = 1.0 / math.sqrt(count)
            score += cat_w * sev_w * diminishing

        # Context multiplier
        context_multipliers = {
            "github_title": 1.5,
            "github_body": 1.2,
            "developer": 0.5,
            "general": 1.0,
        }
        score *= context_multipliers.get(context, 1.0)

        return score

    @staticmethod
    def _score_to_level(score: float) -> ThreatLevel:
        if score >= 8.0:
            return ThreatLevel.CRITICAL
        elif score >= 5.0:
            return ThreatLevel.DANGEROUS
        elif score >= 2.0:
            return ThreatLevel.SUSPICIOUS
        return ThreatLevel.SAFE

    @staticmethod
    def _calculate_confidence(matches: List[PatternMatch]) -> float:
        if not matches:
            return 0.0
        severity_map = {"low": 0.3, "medium": 0.5, "high": 0.7, "critical": 0.9}
        max_severity = max(severity_map.get(m.severity, 0.3) for m in matches)
        count_factor = min(1.0, len(matches) * 0.15)
        return min(1.0, max(max_severity, count_factor))

    def _sanitize(self, text: str, matches: List[PatternMatch]) -> str:
        """Replace matched patterns with placeholders."""
        sanitized = text
        replacements = {
            "execution": "[BLOCKED_COMMAND]",
            "injection": "[BLOCKED_INJECTION]",
            "social": "[FLAGGED_SOCIAL_ENG]",
            "filesystem": "[BLOCKED_FILE_OP]",
            "network": "[BLOCKED_NETWORK]",
            "encoding": "[BLOCKED_ENCODING]",
            "rendering": "[BLOCKED_CHAR]",
            "container": "[BLOCKED_CONTAINER]",

        }
        seen_patterns: set = set()
        for m in matches:
            if m.pattern in seen_patterns:
                continue
            seen_patterns.add(m.pattern)
            replacement = replacements.get(m.category, "[BLOCKED]")
            try:
                compiled = re.compile(m.pattern, re.IGNORECASE | re.MULTILINE)
                sanitized = compiled.sub(replacement, sanitized)
            except re.error:
                continue
        return sanitized

    def _check_rate_limit(self, source_id: str) -> bool:
        with self._lock:
            now = time.monotonic()
            cutoff = now - 60.0
            if source_id in self._rate_tracker:
                self._rate_tracker[source_id] = [
                    t for t in self._rate_tracker[source_id] if t > cutoff
                ]
            else:
                self._rate_tracker[source_id] = []
            if len(self._rate_tracker[source_id]) >= self._rate_limit:
                return True
            self._rate_tracker[source_id].append(now)
            return False

    @staticmethod
    def _safe_result(start_time: float) -> DetectionResult:
        elapsed = (time.monotonic() - start_time) * 1000
        return DetectionResult(
            threat_level=ThreatLevel.SAFE,
            confidence=0.0,
            patterns_detected=(),
            sanitized_text=None,
            risk_score=0.0,
            execution_commands=(),
            analysis_time_ms=elapsed,
        )

    @staticmethod
    def _error_result(message: str, start_time: float) -> DetectionResult:
        elapsed = (time.monotonic() - start_time) * 1000
        return DetectionResult(
            threat_level=ThreatLevel.SAFE,
            confidence=0.0,
            patterns_detected=(PatternMatch(
                category="error",
                pattern="",
                severity="low",
                match=message,
            ),),
            sanitized_text=None,
            risk_score=0.0,
            execution_commands=(),
            analysis_time_ms=elapsed,
        )


# --- CLI ---

def _build_cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agent_guard",
        description="AgentGuard: Pattern-based prompt injection and command injection detection.",
    )
    parser.add_argument("--version", action="version", version=f"AgentGuard {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # analyze
    analyze_p = subparsers.add_parser("analyze", help="Analyze text for threats")
    analyze_p.add_argument("text", nargs="?", default=None, help="Text to analyze")
    analyze_p.add_argument("--stdin", action="store_true", help="Read text from stdin")
    analyze_p.add_argument(
        "--context",
        default="general",
        choices=["general", "github_title", "github_body", "developer"],
        help="Analysis context (default: general)",
    )
    analyze_p.add_argument("--json", action="store_true", dest="json_output", help="Output as JSON")

    # github-issue
    gh_p = subparsers.add_parser("github-issue", help="Analyze a GitHub issue")
    gh_p.add_argument("--title", required=True, help="Issue title")
    gh_p.add_argument("--body", required=True, help="Issue body")
    gh_p.add_argument("--json", action="store_true", dest="json_output", help="Output as JSON")

    # report
    report_p = subparsers.add_parser("report", help="Show pattern statistics")
    report_p.add_argument("--json", action="store_true", dest="json_output", help="Output as JSON")

    # version (also available as subcommand)
    subparsers.add_parser("version", help="Show version")

    return parser


def _run_analyze(args: argparse.Namespace) -> int:
    """Run the analyze subcommand."""
    if args.stdin:
        text = sys.stdin.read()
    elif args.text is not None:
        text = args.text
    else:
        print("Error: provide text as argument or use --stdin", file=sys.stderr)
        return 1

    guard = AgentGuard()
    result = guard.analyze_text(text, context=args.context)

    if args.json_output:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(f"Threat Level: {result.threat_level.value}")
        print(f"Risk Score:   {result.risk_score:.2f}")
        print(f"Confidence:   {result.confidence:.2f}")
        print(f"Analysis:     {result.analysis_time_ms:.2f}ms")
        if result.patterns_detected:
            print(f"Patterns:     {len(result.patterns_detected)} matched")
            for p in result.patterns_detected:
                print(f"  [{p.severity}] {p.category}: {p.match}")
        if result.execution_commands:
            print(f"Commands:     {', '.join(result.execution_commands)}")
        if result.sanitized_text:
            print(f"\nSanitized:\n{result.sanitized_text}")
        print(f"\nRecommendation: {_get_recommendation(result.threat_level)}")
    return 0


def _run_github_issue(args: argparse.Namespace) -> int:
    """Run the github-issue subcommand."""
    guard = AgentGuard()
    analysis = guard.analyze_github_issue(args.title, args.body)

    if args.json_output:
        output = {
            "version": __version__,
            "title_analysis": analysis["title_analysis"].to_dict(),
            "body_analysis": analysis["body_analysis"].to_dict(),
            "overall_threat": analysis["overall_threat"].value,
            "combined_risk_score": round(analysis["combined_risk_score"], 2),
            "clinejection_risk": analysis["clinejection_risk"],
            "should_block": analysis["should_block"],
            "recommendation": analysis["recommendation"],
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"Overall Threat:   {analysis['overall_threat'].value}")
        print(f"Risk Score:       {analysis['combined_risk_score']:.2f}")
        print(f"Clinejection Risk: {analysis['clinejection_risk']}")
        print(f"Should Block:     {analysis['should_block']}")
        print(f"Recommendation:   {analysis['recommendation']}")
        if analysis["title_analysis"].patterns_detected:
            print(f"\nTitle patterns:")
            for p in analysis["title_analysis"].patterns_detected:
                print(f"  [{p.severity}] {p.category}: {p.match}")
        if analysis["body_analysis"].patterns_detected:
            print(f"\nBody patterns:")
            for p in analysis["body_analysis"].patterns_detected:
                print(f"  [{p.severity}] {p.category}: {p.match}")
    return 0


def _run_report(args: argparse.Namespace) -> int:
    """Run the report subcommand."""
    guard = AgentGuard()
    counts = guard.get_pattern_counts()
    total = sum(counts.values())

    if args.json_output:
        print(json.dumps({
            "version": __version__,
            "total_patterns": total,
            "pattern_counts": counts,
        }, indent=2))
    else:
        print(f"AgentGuard v{__version__}")
        print(f"Total patterns: {total}")
        for cat, count in sorted(counts.items()):
            print(f"  {cat}: {count}")
    return 0


def main() -> int:
    parser = _build_cli()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    if args.command == "version":
        print(f"AgentGuard {__version__}")
        return 0

    handlers = {
        "analyze": _run_analyze,
        "github-issue": _run_github_issue,
        "report": _run_report,
    }

    handler = handlers.get(args.command)
    if handler:
        return handler(args)

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
