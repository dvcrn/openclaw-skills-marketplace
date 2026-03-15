"""Guardian context signal detection for severity score adjustment.

These modifiers adjust the raw threat score based on the surrounding context
of a detected pattern, reducing false positives while amplifying true threats.

Rules applied (in order, additive):
  1. Code-block wrapping  → reduce score by 20 %
  2. Meta-context words   → reduce score by 15 %
  3. Standalone imperative → increase score by 25 %

Scores are clamped to [0, 100] after all adjustments.
"""

from __future__ import annotations

import re

# Words that indicate explanatory / meta context (pattern documentation, rules,
# test cases) rather than an active attack.
_META_WORD_RE = re.compile(
    r"\b(?:detects?|blocks?|examples?|signatures?|patterns?\s+for|regexes?|rules?|heuristics?)\b",
    re.IGNORECASE,
)

# Imperative verbs commonly seen at the start of prompt-injection commands.
_IMPERATIVE_VERBS = (
    "ignore",
    "bypass",
    "disable",
    "override",
    "reveal",
    "show",
    "dump",
    "print",
    "exfiltrate",
    "leak",
    "send",
    "delete",
)
_STANDALONE_IMPERATIVE_RE = re.compile(
    rf"^\s*(?:{'|'.join(_IMPERATIVE_VERBS)})\b",
    re.IGNORECASE,
)

# Prefixes that indicate the imperative is merely being *discussed*, not issued.
_EXPLANATION_PREFIX_RE = re.compile(
    r"^\s*(?:for example|example|pattern|signature|rule|heuristic|detect|detection|test|unit test|if)\b",
    re.IGNORECASE,
)

# Reduction/increase percentages expressed as integer point deltas.
CODE_BLOCK_REDUCTION = 20
META_WORD_REDUCTION = 15
STANDALONE_IMPERATIVE_BOOST = 25


def is_inside_backticks(text: str, start: int, end: int) -> bool:
    """Return ``True`` when ``text[start:end]`` appears wrapped in inline backticks.

    Searches for a backtick to the left of *start* and one to the right of *end*
    within *text*.  Also accepts triple-backtick fenced code blocks.

    Args:
        text:  The full source text.
        start: Inclusive start of the match span.
        end:   Exclusive end of the match span.
    """
    # Inline backtick check
    left = text.rfind("`", 0, start)
    if left != -1:
        right = text.find("`", end)
        if right != -1 and left < start <= end <= right:
            return True

    # Triple-backtick fenced block check
    fence_open = text.rfind("```", 0, start)
    if fence_open != -1:
        fence_close = text.find("```", end)
        if fence_close != -1 and fence_open < start <= end <= fence_close:
            return True

    return False


def has_meta_context(text: str, match_start: int, context_window: int = 150) -> bool:
    """Return ``True`` if meta/explanatory words appear near *match_start*.

    Looks within *context_window* characters before the match position for
    words like "detects", "example", "signature", "pattern", etc.

    Args:
        text:           Full source text.
        match_start:    Start index of the threat pattern match.
        context_window: How many characters before the match to inspect.
    """
    pre = text[max(0, match_start - context_window): match_start]
    return bool(_META_WORD_RE.search(pre))


def is_standalone_imperative(text: str, match_start: int) -> bool:
    """Return ``True`` when the match looks like a bare, uncontextualised command.

    Extracts the line containing *match_start* and checks whether it:
    - starts with an imperative verb,
    - is not preceded by an explanatory prefix,
    - is not inside backtick code spans, and
    - is short enough to be a direct command (≤ 12 words).

    Args:
        text:        Full source text.
        match_start: Start index of the threat pattern match.
    """
    line_start = text.rfind("\n", 0, match_start)
    line_start = 0 if line_start == -1 else line_start + 1
    line_end = text.find("\n", match_start)
    line_end = len(text) if line_end == -1 else line_end
    line = text[line_start:line_end].strip()

    if not line:
        return False
    if _EXPLANATION_PREFIX_RE.search(line):
        return False
    if is_inside_backticks(text, match_start, match_start + max(1, len(line))):
        return False

    words = re.findall(r"\b[\w'-]+\b", line.lower())
    if not words or len(words) > 12:
        return False

    return bool(_STANDALONE_IMPERATIVE_RE.search(line))


def apply_context_modifiers(score: int, text: str, match_start: int, match_end: int) -> int:
    """Return the adjusted score after applying all context modifiers.

    Applies the following adjustments (clamped to [0, 100]):
    - Subtract :data:`CODE_BLOCK_REDUCTION` if the match is inside backticks.
    - Subtract :data:`META_WORD_REDUCTION` if meta-context words precede the match.
    - Add :data:`STANDALONE_IMPERATIVE_BOOST` if the match looks like a bare command.

    Args:
        score:       Raw threat score before context adjustment.
        text:        Full source text.
        match_start: Start of the matched pattern span.
        match_end:   End of the matched pattern span.

    Returns:
        Adjusted score in [0, 100].
    """
    adjusted = score

    if is_inside_backticks(text, match_start, match_end):
        adjusted -= CODE_BLOCK_REDUCTION

    if has_meta_context(text, match_start):
        adjusted -= META_WORD_REDUCTION

    if is_standalone_imperative(text, match_start):
        adjusted += STANDALONE_IMPERATIVE_BOOST

    return max(0, min(100, adjusted))
