#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prepare data for replying to a GitCode issue.
Read-only: fetches issue, comments, history, DeepWiki; outputs JSON. No comments posted.

Usage:
  python prepare_issue_reply.py --issue-url "https://gitcode.com/owner/repo/issues/123"
"""

import sys
import re
import json
import argparse
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import quote

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
CONFIG_FILE = SKILL_ROOT / "config.json"
PROMPTS_DIR = SKILL_ROOT / "references" / "prompts"

sys.path.insert(0, str(SCRIPT_DIR))
from _common import get_token, print_json, parse_issue_url, api_get, init_windows_encoding

CONTENT_MAX_CHARS = 3000
HISTORY_ISSUES_MAX = 100
ONE_YEAR_DAYS = 365
DEEPWIKI_TIMEOUT = 120
DEEPWIKI_MAX_RETRIES = 3

BOT_INDICATORS = ["bot", "[bot]", "ci-bot", "gitcode-bot", "webhook"]


def load_config():
    cfg = {
        "content_max_chars": CONTENT_MAX_CHARS,
        "history_issues_max": HISTORY_ISSUES_MAX,
        "deepwiki_timeout": DEEPWIKI_TIMEOUT,
        "deepwiki_max_retries": DEEPWIKI_MAX_RETRIES,
        "dry_run": False,
    }
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg.update(json.load(f))
        except Exception as e:
            sys.stderr.write("Warning: failed to load config.json: %s\n" % e)
    return cfg


def strip_non_text(text):
    if not text or not isinstance(text, str):
        return ""
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)", "[图片已省略]", text)
    text = re.sub(
        r"https?://[^\s)]+\.(?:png|jpe?g|gif|webp|bmp|svg)(?:\?[^\s)]*)?",
        "[图片链接已省略]", text, flags=re.I,
    )
    return text.strip()


def _is_bot_user(user_dict):
    """Detect bot accounts by type field or login name patterns."""
    if not user_dict:
        return False
    if (user_dict.get("type") or "").lower() == "bot":
        return True
    login = (user_dict.get("login") or user_dict.get("username") or "").lower()
    return any(ind in login for ind in BOT_INDICATORS)


def _is_substantive_comment(body_text):
    """A comment is substantive if it's non-empty, non-command, and >= 10 chars."""
    if not body_text:
        return False
    stripped = body_text.strip()
    if stripped.startswith("/"):
        return False
    return len(stripped) >= 10


def deepwiki_single(repo, question, timeout=120, max_retries=3):
    """Single DeepWiki query. Returns (answer_text, status) where status is ok|empty|failed|skipped."""
    if not HAS_REQUESTS or "/" not in repo:
        return "", "skipped"
    url_mcp = "https://mcp.deepwiki.com/mcp"
    headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
    init_payload = {"jsonrpc": "2.0", "method": "initialize", "params": {
        "protocolVersion": "2024-11-05", "capabilities": {},
        "clientInfo": {"name": "gitcode-issue-reply", "version": "1.0.0"},
    }, "id": 1}
    ask_payload = {"jsonrpc": "2.0", "method": "tools/call", "params": {
        "name": "ask_question", "arguments": {"repoName": repo, "question": question},
    }, "id": 1}
    last_error = None
    for attempt in range(max_retries + 1):
        try:
            requests.post(url_mcp, json=init_payload, headers=headers, timeout=timeout)
            resp = requests.post(url_mcp, json=ask_payload, headers=headers, timeout=timeout)
            resp.raise_for_status()
            data = resp.json()
            if data.get("error"):
                return "", "error"
            result = data.get("result", {})
            if isinstance(result, dict):
                content = result.get("content", [])
                if isinstance(content, list):
                    texts = [c.get("text", "") for c in content
                             if isinstance(c, dict) and c.get("type") == "text"]
                    answer = "\n".join(texts)
                    return answer, ("ok" if answer else "empty")
                sc = result.get("structuredContent", {})
                if sc.get("result"):
                    return sc["result"], "ok"
            return (str(result) if result else ""), "empty"
        except Exception as e:
            last_error = str(e)
            if attempt < max_retries:
                wait_time = 2 ** attempt
                sys.stderr.write("DeepWiki retry %s/%s after %ss: %s\n" % (
                    attempt + 1, max_retries, wait_time, last_error))
                time.sleep(wait_time)
    sys.stderr.write("DeepWiki failed after %s attempts: %s\n" % (max_retries + 1, last_error))
    return "", "failed"


def main():
    parser = argparse.ArgumentParser(
        description="Prepare issue reply data (read-only, no comments posted)")
    parser.add_argument("--issue-url", required=True, help="Full issue URL")
    args = parser.parse_args()

    init_windows_encoding()

    token = get_token()
    if not token:
        print_json({"status": "error",
                     "message": "GITCODE_TOKEN not configured. "
                                "Visit https://gitcode.com/setting/token-classic to create one."})
        sys.exit(1)

    try:
        owner, repo, number = parse_issue_url(args.issue_url)
    except ValueError as e:
        print_json({"status": "error", "message": str(e)})
        sys.exit(1)

    config = load_config()
    content_max = (config.get("issue_content_max_chars")
                   or config.get("content_max_chars", CONTENT_MAX_CHARS))
    history_max = (config.get("history_issues_limit")
                   or config.get("history_issues_max", HISTORY_ISSUES_MAX))

    # --- Fetch issue ---
    try:
        issue = api_get(token, f"repos/{owner}/{repo}/issues/{number}")
    except HTTPError as e:
        body = e.read().decode("utf-8", errors="replace") if e.fp else ""
        print_json({"status": "error", "message": f"Failed to fetch issue: {e.code} {body}"})
        sys.exit(1)

    # --- Fetch comments ---
    comments = []
    page = 1
    while True:
        try:
            batch = api_get(token,
                            f"repos/{owner}/{repo}/issues/{number}/comments?per_page=100&page={page}")
        except Exception as e:
            sys.stderr.write("Warning: failed to fetch comments page %d: %s\n" % (page, e))
            break
        if not isinstance(batch, list) or not batch:
            break
        comments.extend(batch)
        if len(batch) < 100:
            break
        page += 1
        if page > 10:
            break

    author_id = (issue.get("user") or {}).get("id")
    author_login = ((issue.get("user") or {}).get("login")
                    or (issue.get("user") or {}).get("username") or "")

    # --- Check for substantive non-author, non-bot replies ---
    has_other_reply = False
    for c in comments:
        u = c.get("user") or {}
        if _is_bot_user(u):
            continue
        uid = u.get("id")
        ulogin = u.get("login") or u.get("username") or ""
        if uid == author_id or (ulogin and ulogin == author_login):
            continue
        if _is_substantive_comment(c.get("body", "")):
            has_other_reply = True
            break

    if has_other_reply:
        print_json({
            "status": "already_replied",
            "owner": owner, "repo": repo, "issue_number": number,
            "message": "该 Issue 已有其他人回复，已跳过",
        })
        return

    # --- Label decision (Agent will act on this, script does NOT post) ---
    has_label_comment = any("/label add" in (c.get("body") or "").lower() for c in comments)
    dry_run = config.get("dry_run", False)
    label_needed = not has_label_comment and not dry_run

    # --- Build issue content text ---
    parts = [issue.get("title") or "", "\n\n", issue.get("body") or ""]
    for c in sorted(comments, key=lambda x: (x.get("created_at") or "")):
        body_text = (c.get("body") or "").strip()
        if body_text.startswith("/"):
            continue
        parts.append("\n\n[评论] ")
        parts.append((c.get("user") or {}).get("login")
                      or (c.get("user") or {}).get("username") or "?")
        parts.append(": ")
        parts.append(body_text)
    issue_content_plain = strip_non_text("".join(parts))

    if len(issue_content_plain) > content_max:
        issue_content_plain = issue_content_plain[:content_max] + "\n\n[内容已截断]"

    # --- Fetch history issues (with since for server-side filtering) ---
    now = datetime.now(timezone.utc)
    one_year_ago = (now - timedelta(days=ONE_YEAR_DAYS)).strftime("%Y-%m-%dT%H:%M:%SZ")
    history_issues = []
    page = 1
    while len(history_issues) < history_max:
        try:
            items = api_get(
                token,
                f"repos/{owner}/{repo}/issues?state=all&since={one_year_ago}"
                f"&per_page=100&page={page}")
        except Exception as e:
            sys.stderr.write("Warning: failed to fetch history page %d: %s\n" % (page, e))
            break
        if not isinstance(items, list) or not items:
            break
        for i in items:
            if i.get("number") == number:
                continue
            if "CVE" in (i.get("title") or "").upper():
                continue
            num = i.get("number")
            if num is not None:
                history_issues.append({
                    "number": int(num) if isinstance(num, str) else num,
                    "title": (i.get("title") or "")[:200],
                })
            if len(history_issues) >= history_max:
                break
        if len(items) < 100:
            break
        page += 1
        if page > 10:
            break

    # --- DeepWiki query ---
    deepwiki_answer = ""
    deepwiki_status = "skipped"
    if HAS_REQUESTS:
        deepwiki_query = ((issue.get("title") or "") + "\n"
                          + ((issue.get("body") or "")[:500]))
        deepwiki_answer, deepwiki_status = deepwiki_single(
            f"{owner}/{repo}",
            deepwiki_query.strip(),
            timeout=config.get("deepwiki_timeout", DEEPWIKI_TIMEOUT),
            max_retries=config.get("deepwiki_max_retries", DEEPWIKI_MAX_RETRIES),
        )

    # --- New contributor check ---
    is_new_contributor = True
    try:
        if author_login:
            check_issues = api_get(
                token,
                f"repos/{owner}/{repo}/issues?state=all"
                f"&creator={quote(author_login)}&per_page=5")
            other_issues = [i for i in (check_issues or []) if i.get("number") != number]
            if other_issues:
                is_new_contributor = False
        if is_new_contributor and author_login:
            check_pulls = api_get(
                token,
                f"repos/{owner}/{repo}/pulls?state=all&per_page=20")
            for p in (check_pulls or []):
                u = p.get("user") or {}
                if (u.get("id") == author_id
                        or (u.get("login") or u.get("username") or "") == author_login):
                    is_new_contributor = False
                    break
    except Exception as e:
        sys.stderr.write("Warning: new contributor check failed: %s\n" % e)

    labels = [lb.get("name") for lb in (issue.get("labels") or []) if lb.get("name")]
    meta = {
        "title": (issue.get("title") or "")[:500],
        "labels": labels,
        "is_new_contributor": is_new_contributor,
    }

    # --- Build prompts ---
    history_fmt = "\n".join(
        "#%s %s" % (h["number"], (h.get("title") or "").strip())
        for h in history_issues)
    prompt_similarity = ""
    prompt_draft_partial = ""
    if PROMPTS_DIR.exists():
        sim_path = PROMPTS_DIR / "similarity.txt"
        if sim_path.exists():
            try:
                tpl = sim_path.read_text(encoding="utf-8")
                prompt_similarity = (tpl
                                     .replace("{issue_content_plain}", issue_content_plain)
                                     .replace("{history_issues_formatted}", history_fmt))
            except Exception as e:
                sys.stderr.write("Warning: failed to read similarity prompt: %s\n" % e)
        draft_path = PROMPTS_DIR / "draft_reply.txt"
        if draft_path.exists():
            try:
                issue_base_url = "https://gitcode.com/%s/%s" % (owner, repo)
                tpl = draft_path.read_text(encoding="utf-8")
                tpl = tpl.replace("{issue_content_plain}", issue_content_plain)
                tpl = tpl.replace("{issue_metadata.title}", meta["title"])
                tpl = tpl.replace("{issue_metadata.labels}",
                                  ", ".join(meta["labels"]) if meta["labels"] else "（无）")
                tpl = tpl.replace("{issue_metadata.is_new_contributor}",
                                  "是" if meta["is_new_contributor"] else "否")
                tpl = tpl.replace("{deepwiki_answer}",
                                  deepwiki_answer if deepwiki_answer else "（无）")
                tpl = tpl.replace("{issue_base_url}", issue_base_url)
                prompt_draft_partial = tpl
            except Exception as e:
                sys.stderr.write("Warning: failed to read draft prompt: %s\n" % e)

    out = {
        "status": "ok",
        "owner": owner,
        "repo": repo,
        "issue_number": number,
        "issue_url": args.issue_url,
        "issue_content_plain": issue_content_plain,
        "issue_metadata": meta,
        "history_issues": history_issues,
        "deepwiki_answer": deepwiki_answer,
        "deepwiki_status": deepwiki_status,
        "label_needed": label_needed,
        "prompt_similarity": prompt_similarity,
        "prompt_draft_partial": prompt_draft_partial,
    }
    print_json(out)


if __name__ == "__main__":
    main()
