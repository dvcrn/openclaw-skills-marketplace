"""Core scanning engine for VEXT Shield.

Performs static analysis of OpenClaw skills for prompt injection,
data exfiltration, persistence manipulation, privilege escalation,
supply chain attacks, semantic worms, reverse shells, and cryptomining.

Uses pattern matching (regex + literal), Python AST analysis, and
encoded content detection.
"""

from __future__ import annotations

import ast
import json
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from . import utils


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class Finding:
    """A single security finding from a scan."""

    id: str                    # Pattern ID, e.g. "PI-001"
    severity: str              # CRITICAL / HIGH / MEDIUM / LOW / INFO
    category: str              # prompt_injection, data_exfiltration, etc.
    subcategory: str           # direct, encoded, indirect, etc.
    name: str                  # Human-readable pattern name
    description: str           # What was found and why it matters
    file_path: str             # Relative path within skill directory
    line_number: int | None    # Line where pattern was found (1-based)
    matched_text: str          # The actual text that matched
    confidence: float          # 0.0 - 1.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "severity": self.severity,
            "category": self.category,
            "subcategory": self.subcategory,
            "name": self.name,
            "description": self.description,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "matched_text": self.matched_text[:200],  # Truncate for reports
            "confidence": self.confidence,
        }


@dataclass
class ScanResult:
    """Aggregated scan results for a single skill."""

    skill_name: str
    skill_path: str
    risk_level: str            # CRITICAL / HIGH / MEDIUM / LOW / CLEAN
    findings: list[Finding] = field(default_factory=list)
    scan_duration_ms: int = 0
    files_scanned: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "skill_name": self.skill_name,
            "skill_path": self.skill_path,
            "risk_level": self.risk_level,
            "findings_count": len(self.findings),
            "findings": [f.to_dict() for f in self.findings],
            "scan_duration_ms": self.scan_duration_ms,
            "files_scanned": self.files_scanned,
        }


# ---------------------------------------------------------------------------
# Compiled signature cache
# ---------------------------------------------------------------------------

@dataclass
class _CompiledPattern:
    """A pre-compiled pattern ready for matching."""

    id: str
    name: str
    description: str
    regex: re.Pattern[str]
    category: str
    subcategory: str
    severity: str
    is_literal: bool


# ---------------------------------------------------------------------------
# Dangerous AST node definitions
# ---------------------------------------------------------------------------

# Functions that are dangerous when called directly
_DANGEROUS_CALLS: dict[str, tuple[str, str]] = {
    "eval": ("SC-022", "Evaluates arbitrary code string"),
    "exec": ("SC-023", "Executes arbitrary code string"),
    "compile": ("SC-024", "Compiles code string for execution"),
    "__import__": ("SC-021", "Dynamically imports module"),
}

# Dangerous attribute access patterns: (module, attr) -> (id, desc)
_DANGEROUS_ATTRS: dict[tuple[str, str], tuple[str, str]] = {
    ("os", "system"): ("SC-022", "Executes shell command via os.system"),
    ("os", "popen"): ("SC-022", "Opens shell pipe via os.popen"),
    ("os", "exec"): ("SC-022", "Replaces process via os.exec*"),
    ("os", "execvp"): ("SC-022", "Replaces process via os.execvp"),
    ("os", "execve"): ("SC-022", "Replaces process via os.execve"),
    ("os", "spawn"): ("SC-022", "Spawns process via os.spawn*"),
    ("os", "spawnl"): ("SC-022", "Spawns process via os.spawnl"),
    ("os", "dup2"): ("RS-012", "Duplicates file descriptor (reverse shell setup)"),
    ("subprocess", "call"): ("RS-013", "Calls subprocess"),
    ("subprocess", "run"): ("RS-013", "Runs subprocess"),
    ("subprocess", "Popen"): ("RS-013", "Opens subprocess pipe"),
    ("subprocess", "check_output"): ("RS-013", "Runs subprocess with output capture"),
    ("subprocess", "check_call"): ("RS-013", "Runs subprocess with error check"),
    ("importlib", "import_module"): ("SC-020", "Dynamically imports module"),
    ("ctypes", "CDLL"): ("SC-027", "Loads native C library"),
    ("ctypes", "cdll"): ("SC-027", "Loads native C library"),
    ("ctypes", "windll"): ("SC-027", "Loads Windows DLL"),
    ("socket", "connect"): ("DE-070", "Establishes socket connection"),
    ("socket", "create_connection"): ("DE-070", "Creates socket connection"),
    ("urllib", "urlopen"): ("DE-066", "Opens URL connection"),
    ("pickle", "loads"): ("SC-030", "Deserializes pickled data (arbitrary code exec)"),
    ("pickle", "load"): ("SC-030", "Deserializes pickled data (arbitrary code exec)"),
    ("marshal", "loads"): ("SC-029", "Deserializes Python bytecode"),
    ("pty", "spawn"): ("RS-011", "Spawns PTY shell"),
}

# Module-level imports that are suspicious
_SUSPICIOUS_IMPORTS: dict[str, tuple[str, str]] = {
    "ctypes": ("SC-027", "Imports native C library interface"),
    "pickle": ("SC-030", "Imports pickle (arbitrary code execution risk)"),
    "marshal": ("SC-029", "Imports marshal (bytecode deserialization)"),
    "pty": ("RS-011", "Imports PTY module (shell spawning)"),
}


# ---------------------------------------------------------------------------
# Scanner Core
# ---------------------------------------------------------------------------

class ScannerCore:
    """Core scanning engine for OpenClaw skill security analysis.

    Loads threat signatures and performs multi-layered analysis:
    1. Text pattern matching (regex + literal)
    2. Python AST analysis for dangerous function calls
    3. Encoded content detection (base64, ROT13, unicode homoglyphs)
    """

    def __init__(self, signatures_path: Path | None = None) -> None:
        if signatures_path is None:
            signatures_path = Path(__file__).parent / "threat_signatures.json"

        with open(signatures_path, "r", encoding="utf-8") as f:
            self._raw_signatures = json.load(f)

        self._compiled: list[_CompiledPattern] = []
        self._compile_patterns()

    def _compile_patterns(self) -> None:
        """Pre-compile all patterns from the signature database."""
        for cat_id, cat_data in self._raw_signatures.get("categories", {}).items():
            severity_default = cat_data.get("severity_default", "medium").upper()

            for sub_id, sub_data in cat_data.get("subcategories", {}).items():
                for pat in sub_data.get("patterns", []):
                    pattern_str = pat["pattern"]
                    is_literal = pat.get("pattern_type", "regex") == "literal"

                    if is_literal:
                        regex = re.compile(re.escape(pattern_str), re.IGNORECASE)
                    else:
                        regex = re.compile(pattern_str, re.IGNORECASE)

                    self._compiled.append(_CompiledPattern(
                        id=pat["id"],
                        name=pat["name"],
                        description=pat["description"],
                        regex=regex,
                        category=cat_id,
                        subcategory=sub_id,
                        severity=severity_default,
                        is_literal=is_literal,
                    ))

    # -------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------

    def scan_skill(self, skill_dir: Path) -> ScanResult:
        """Scan an entire skill directory for security issues."""
        start = time.monotonic()
        skill_name = utils.get_skill_name(skill_dir)
        all_findings: list[Finding] = []
        files_scanned = 0

        for file_path in sorted(skill_dir.rglob("*")):
            if not file_path.is_file():
                continue
            if not utils.is_scannable_file(file_path):
                continue

            findings = self.scan_file(file_path, skill_dir)
            all_findings.extend(findings)
            files_scanned += 1

        # Deduplicate findings (same pattern + same file + same line)
        all_findings = self._deduplicate(all_findings)

        # Calculate risk level
        risk_level = self._calculate_risk_level(all_findings)

        elapsed_ms = int((time.monotonic() - start) * 1000)

        return ScanResult(
            skill_name=skill_name,
            skill_path=str(skill_dir),
            risk_level=risk_level,
            findings=all_findings,
            scan_duration_ms=elapsed_ms,
            files_scanned=files_scanned,
        )

    def scan_file(self, file_path: Path, skill_dir: Path | None = None) -> list[Finding]:
        """Scan a single file for security issues."""
        content = utils.read_file_safe(file_path)
        if content is None:
            return []

        rel_path = str(file_path.relative_to(skill_dir)) if skill_dir else str(file_path)

        findings: list[Finding] = []

        # Layer 1: Text pattern matching
        findings.extend(self._scan_text_patterns(content, rel_path))

        # Layer 2: Python AST analysis
        if file_path.suffix == ".py":
            findings.extend(self._scan_python_ast(content, rel_path))

        # Layer 3: Encoded content detection
        findings.extend(self._scan_encoded_content(content, rel_path))

        return findings

    # -------------------------------------------------------------------
    # Layer 1: Text pattern matching
    # -------------------------------------------------------------------

    def _scan_text_patterns(self, content: str, file_path: str) -> list[Finding]:
        """Match all compiled patterns against file content."""
        findings: list[Finding] = []
        lines = content.split("\n")

        for cp in self._compiled:
            for line_num, line in enumerate(lines, 1):
                match = cp.regex.search(line)
                if match:
                    # Compute confidence based on match context
                    confidence = self._compute_confidence(cp, line, match)

                    findings.append(Finding(
                        id=cp.id,
                        severity=cp.severity,
                        category=cp.category,
                        subcategory=cp.subcategory,
                        name=cp.name,
                        description=cp.description,
                        file_path=file_path,
                        line_number=line_num,
                        matched_text=match.group()[:200],
                        confidence=confidence,
                    ))
                    # Only report first match per pattern per file for non-critical
                    if cp.severity != "CRITICAL":
                        break

        return findings

    def _compute_confidence(
        self, pattern: _CompiledPattern, line: str, match: re.Match[str]
    ) -> float:
        """Compute confidence score for a pattern match.

        Considers:
        - Whether the match is in a comment
        - Pattern specificity (literal vs regex)
        - Category severity
        """
        confidence = 0.7  # Base confidence

        # Boost for literal matches (more specific)
        if pattern.is_literal:
            confidence += 0.1

        # Reduce for matches in comments
        stripped = line.lstrip()
        if stripped.startswith("#") or stripped.startswith("//") or stripped.startswith("<!--"):
            confidence -= 0.2

        # Boost for critical categories
        if pattern.severity == "CRITICAL":
            confidence += 0.1

        # Boost for longer matches (more specific)
        if len(match.group()) > 20:
            confidence += 0.1

        return min(1.0, max(0.1, confidence))

    # -------------------------------------------------------------------
    # Layer 2: Python AST analysis
    # -------------------------------------------------------------------

    def _scan_python_ast(self, content: str, file_path: str) -> list[Finding]:
        """Analyze Python source code AST for dangerous patterns."""
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return []

        findings: list[Finding] = []

        for node in ast.walk(tree):
            # Check function calls
            if isinstance(node, ast.Call):
                finding = self._check_call_node(node, file_path)
                if finding:
                    findings.append(finding)

            # Check imports
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in _SUSPICIOUS_IMPORTS:
                        pat_id, desc = _SUSPICIOUS_IMPORTS[alias.name]
                        findings.append(Finding(
                            id=pat_id,
                            severity="MEDIUM",
                            category="supply_chain",
                            subcategory="dynamic_import",
                            name=f"Suspicious import: {alias.name}",
                            description=desc,
                            file_path=file_path,
                            line_number=getattr(node, "lineno", None),
                            matched_text=f"import {alias.name}",
                            confidence=0.5,
                        ))

            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if module in _SUSPICIOUS_IMPORTS:
                    pat_id, desc = _SUSPICIOUS_IMPORTS[module]
                    names = ", ".join(a.name for a in node.names)
                    findings.append(Finding(
                        id=pat_id,
                        severity="MEDIUM",
                        category="supply_chain",
                        subcategory="dynamic_import",
                        name=f"Suspicious import from {module}",
                        description=desc,
                        file_path=file_path,
                        line_number=getattr(node, "lineno", None),
                        matched_text=f"from {module} import {names}",
                        confidence=0.5,
                    ))

        return findings

    def _check_call_node(self, node: ast.Call, file_path: str) -> Finding | None:
        """Check if an AST Call node represents a dangerous function call."""
        func = node.func

        # Direct calls: eval(...), exec(...)
        if isinstance(func, ast.Name) and func.id in _DANGEROUS_CALLS:
            pat_id, desc = _DANGEROUS_CALLS[func.id]
            return Finding(
                id=pat_id,
                severity="CRITICAL",
                category="supply_chain",
                subcategory="dynamic_import",
                name=f"Dangerous call: {func.id}()",
                description=desc,
                file_path=file_path,
                line_number=getattr(node, "lineno", None),
                matched_text=f"{func.id}(...)",
                confidence=0.9,
            )

        # Attribute calls: os.system(...), subprocess.Popen(...)
        if isinstance(func, ast.Attribute):
            module_name = self._resolve_attribute_module(func)
            if module_name:
                key = (module_name, func.attr)
                if key in _DANGEROUS_ATTRS:
                    pat_id, desc = _DANGEROUS_ATTRS[key]
                    return Finding(
                        id=pat_id,
                        severity="HIGH",
                        category="supply_chain",
                        subcategory="dynamic_import",
                        name=f"Dangerous call: {module_name}.{func.attr}()",
                        description=desc,
                        file_path=file_path,
                        line_number=getattr(node, "lineno", None),
                        matched_text=f"{module_name}.{func.attr}(...)",
                        confidence=0.85,
                    )

        return None

    @staticmethod
    def _resolve_attribute_module(node: ast.Attribute) -> str | None:
        """Resolve the module name from an attribute access chain."""
        parts: list[str] = []
        current: ast.expr = node.value
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
            parts.reverse()
            return ".".join(parts)
        return None

    # -------------------------------------------------------------------
    # Layer 3: Encoded content detection
    # -------------------------------------------------------------------

    def _scan_encoded_content(self, content: str, file_path: str) -> list[Finding]:
        """Detect encoded content that may hide malicious instructions."""
        findings: list[Finding] = []

        # Check for suspicious base64 content
        b64_results = utils.decode_base64_strings(content)
        for result in b64_results:
            decoded = result["decoded"].lower()
            # Check if decoded content contains suspicious keywords
            suspicious_keywords = [
                "ignore", "override", "system", "execute", "eval", "exec",
                "password", "secret", "token", "api_key", "curl", "wget",
                "socket", "connect", "reverse", "shell", "/bin/sh", "/bin/bash",
                "subprocess", "import os",
            ]
            for keyword in suspicious_keywords:
                if keyword in decoded:
                    findings.append(Finding(
                        id="PI-030",
                        severity="CRITICAL",
                        category="prompt_injection",
                        subcategory="encoded",
                        name=f"Base64-encoded suspicious content ({keyword})",
                        description=f"Base64-encoded text decodes to content containing '{keyword}'",
                        file_path=file_path,
                        line_number=None,
                        matched_text=f"Encoded: {result['encoded'][:60]}... Decoded: {result['decoded'][:60]}...",
                        confidence=0.85,
                    ))
                    break

        # Check for ROT13-encoded suspicious content
        rot13_results = utils.detect_rot13(content)
        for result in rot13_results:
            findings.append(Finding(
                id="PI-034",
                severity="HIGH",
                category="prompt_injection",
                subcategory="encoded",
                name=f"ROT13-encoded suspicious content ({result['keyword']})",
                description=f"ROT13-decoded text contains suspicious keyword: {result['keyword']}",
                file_path=file_path,
                line_number=None,
                matched_text=f"Encoded: {result['encoded'][:60]}... Decoded: {result['decoded'][:60]}...",
                confidence=0.7,
            ))

        # Check for unicode homoglyphs
        homoglyphs = utils.detect_unicode_homoglyphs(content)
        if homoglyphs:
            # Group by line for reporting
            lines_with_homoglyphs: set[int] = set()
            for line_num, char, lookalike, context in homoglyphs:
                if line_num not in lines_with_homoglyphs:
                    lines_with_homoglyphs.add(line_num)
                    desc = "ZERO WIDTH CHARACTER" if not lookalike else f"looks like '{lookalike}'"
                    findings.append(Finding(
                        id="PI-038",
                        severity="HIGH",
                        category="prompt_injection",
                        subcategory="encoded",
                        name=f"Unicode homoglyph ({desc})",
                        description=f"Unicode character that {desc} — may be hiding content",
                        file_path=file_path,
                        line_number=line_num,
                        matched_text=context,
                        confidence=0.75,
                    ))

        # Check for zero-width characters
        zw_chars = utils.detect_zero_width_chars(content)
        if zw_chars:
            lines_with_zw: set[int] = set()
            for line_num, pos, char_name in zw_chars:
                if line_num not in lines_with_zw:
                    lines_with_zw.add(line_num)
                    findings.append(Finding(
                        id="PI-038",
                        severity="HIGH",
                        category="prompt_injection",
                        subcategory="encoded",
                        name=f"Zero-width character: {char_name}",
                        description=f"Zero-width character found that could hide content",
                        file_path=file_path,
                        line_number=line_num,
                        matched_text=f"[{char_name}] at position {pos}",
                        confidence=0.8,
                    ))

        return findings

    # -------------------------------------------------------------------
    # Risk calculation
    # -------------------------------------------------------------------

    @staticmethod
    def _calculate_risk_level(findings: list[Finding]) -> str:
        """Calculate overall risk level based on findings."""
        if not findings:
            return "CLEAN"

        max_severity = 0
        critical_count = 0
        high_count = 0

        for f in findings:
            score = utils.severity_to_score(f.severity)
            max_severity = max(max_severity, score)
            if f.severity == "CRITICAL":
                critical_count += 1
            elif f.severity == "HIGH":
                high_count += 1

        if critical_count > 0:
            return "CRITICAL"
        elif high_count >= 3:
            return "HIGH"
        elif high_count > 0:
            return "HIGH"
        elif max_severity >= 2:
            return "MEDIUM"
        elif max_severity >= 1:
            return "LOW"
        return "CLEAN"

    @staticmethod
    def _deduplicate(findings: list[Finding]) -> list[Finding]:
        """Remove duplicate findings (same ID + file + line)."""
        seen: set[tuple[str, str, int | None]] = set()
        unique: list[Finding] = []
        for f in findings:
            key = (f.id, f.file_path, f.line_number)
            if key not in seen:
                seen.add(key)
                unique.append(f)
        return unique
