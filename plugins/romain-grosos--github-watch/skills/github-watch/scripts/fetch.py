#!/usr/bin/env python3
"""
Jarvis — GitHub Watch
Récupère :
  1. Repos en tendance cette semaine (GitHub Trending, weekly)
  2. Repos actifs par topics configurables (GitHub API, via config.json)

Sortie : JSON sur stdout (wrapped_listing pour LLM inclus)

Usage: python3 fetch.py [--token TOKEN] [--filter-seen]

No external dependencies — stdlib only (urllib.request, html.parser, json).
"""

import json
import sys
import time
import argparse
import os
import re
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).parent))
from untrusted import wrap, build_prompt_header

USER_AGENT = "Jarvis-GHWatch/1.0"


# ---------------------------------------------------------------------------
# Token handling
# ---------------------------------------------------------------------------

def _read_token(token_arg=None):
    """Read GitHub token from arg, env, or config file. Returns None if absent."""
    if token_arg:
        return token_arg
    env_token = os.environ.get("GITHUB_TOKEN")
    if env_token:
        return env_token
    # Try config file
    config_path = Path("~/.openclaw/config/github-watch/config.json").expanduser()
    if config_path.exists():
        try:
            cfg = json.loads(config_path.read_text(encoding="utf-8"))
            token_file = Path(cfg.get("token_path", "")).expanduser()
            if token_file.exists():
                return token_file.read_text(encoding="utf-8").strip()
        except Exception:
            pass
    return None


def _get_headers(token=None):
    h = {"User-Agent": USER_AGENT}
    if token:
        h["Authorization"] = f"Bearer {token}"
        h["Accept"] = "application/vnd.github.v3+json"
    return h


def _http_get(url, headers=None, timeout=20):
    """GET request via urllib, returns (status_code, body_text, response_headers)."""
    hdrs = headers or {"User-Agent": USER_AGENT}
    req = urllib.request.Request(url, headers=hdrs)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read().decode("utf-8", errors="replace")
            return r.status, body, dict(r.headers)
    except urllib.error.HTTPError as e:
        # Do NOT include headers in error message (could leak token)
        body = ""
        try:
            body = e.read().decode("utf-8", errors="replace")[:500]
        except Exception:
            pass
        return e.code, body, {}


# ---------------------------------------------------------------------------
# Trending HTML parser (stdlib html.parser — replaces BeautifulSoup)
# ---------------------------------------------------------------------------

class _TrendingParser(HTMLParser):
    """Parse GitHub Trending page to extract repo data."""

    def __init__(self):
        super().__init__()
        self.repos = []
        self._in_article = False
        self._depth = 0
        self._current = {}
        self._capture_tag = None
        self._capture_text = ""

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        cls = attrs_dict.get("class", "")

        if tag == "article" and "Box-row" in cls:
            self._in_article = True
            self._depth = 0
            self._current = {}

        if not self._in_article:
            return

        self._depth += 1

        # h2 > a => repo path
        if tag == "a" and "href" in attrs_dict:
            href = attrs_dict["href"].strip("/")
            if "/" in href and "name" not in self._current:
                # Check parent context: only take h2 links
                self._current.setdefault("_links", []).append(href)

        # p => description
        if tag == "p":
            self._capture_tag = "description"
            self._capture_text = ""

        # span with itemprop=programmingLanguage
        if tag == "span" and attrs_dict.get("itemprop") == "programmingLanguage":
            self._capture_tag = "language"
            self._capture_text = ""

    def handle_endtag(self, tag):
        if not self._in_article:
            return

        if self._capture_tag and tag in ("p", "span"):
            text = self._capture_text.strip()
            if self._capture_tag == "description" and "description" not in self._current:
                self._current["description"] = text
            elif self._capture_tag == "language" and "language" not in self._current:
                self._current["language"] = text
            self._capture_tag = None
            self._capture_text = ""

        if tag == "article" and self._in_article:
            self._in_article = False
            links = self._current.pop("_links", [])
            # First link with owner/repo pattern is the repo
            for href in links:
                if "/" in href and not href.startswith("http"):
                    self._current["name"] = href
                    self._current["url"] = f"https://github.com/{href}"
                    break
            if "name" in self._current:
                self.repos.append(self._current)
            self._current = {}

    def handle_data(self, data):
        if self._capture_tag:
            self._capture_text += data


def _extract_stars_from_html(html_text, repos):
    """Extract star counts from trending page using regex (more reliable than parser state)."""
    # Pattern for stars gained: "N stars this week/today/month"
    articles = re.split(r'<article[^>]*class="[^"]*Box-row[^"]*"', html_text)

    for i, repo in enumerate(repos):
        if i + 1 < len(articles):
            block = articles[i + 1]
            # Stars gained this period
            gained_m = re.search(r'([\d,]+)\s+stars?\s+(?:this|today|cette)', block)
            repo["stars_gained"] = gained_m.group(1).replace(",", "") if gained_m else "?"
            # Total stars (first octicon-star SVG followed by count)
            star_links = re.findall(r'Link--muted[^>]*>[\s\S]*?([\d,]+)\s*</a>', block)
            repo["stars_total"] = star_links[0].replace(",", "") if star_links else "?"
        else:
            repo["stars_gained"] = "?"
            repo["stars_total"] = "?"
        repo["source"] = "GitHub Trending weekly"


# ---------------------------------------------------------------------------
# Trending
# ---------------------------------------------------------------------------

def fetch_trending(since="weekly", token=None):
    url = f"https://github.com/trending?since={since}"
    status, body, _ = _http_get(url, timeout=20)
    if status != 200:
        raise RuntimeError(f"GitHub Trending returned HTTP {status}")

    parser = _TrendingParser()
    parser.feed(body)
    repos = parser.repos

    _extract_stars_from_html(body, repos)
    return repos


# ---------------------------------------------------------------------------
# API Topics
# ---------------------------------------------------------------------------

def fetch_topic_repos(topic, per_page=25, token=None):
    # Sanitize topic to prevent injection in URL
    safe_topic = re.sub(r'[^a-zA-Z0-9_-]', '', topic)
    url = (
        f"https://api.github.com/search/repositories"
        f"?q=topic:{safe_topic}&sort=updated&order=desc&per_page={per_page}"
    )
    status, body, _ = _http_get(url, headers=_get_headers(token), timeout=20)
    if status == 403:
        print(f"[WARN] Rate limit hit pour topic:{safe_topic}", file=sys.stderr)
        return []
    if status != 200:
        # Do not include body in error (could contain unexpected content)
        raise RuntimeError(f"GitHub API returned HTTP {status} for topic:{safe_topic}")

    data = json.loads(body)
    repos = []
    for item in data.get("items", []):
        repos.append({
            "name": item.get("full_name", "unknown/repo"),
            "url": item.get("html_url", ""),
            "description": (item.get("description") or "").strip(),
            "language": item.get("language") or "",
            "stars_total": item.get("stargazers_count", 0),
            "stars_gained": None,
            "updated": (item.get("pushed_at") or "")[:10],
            "source": f"GitHub topic:{safe_topic}",
        })
    return repos


# ---------------------------------------------------------------------------
# Wrapping LLM-safe
# ---------------------------------------------------------------------------

def wrap_repo(repo, idx):
    lines = [
        f"name: {repo['name']}",
        f"url: {repo['url']}",
        f"description: {repo.get('description', '')}",
        f"language: {repo.get('language', '') or 'N/A'}",
        f"stars: {repo.get('stars_total', '?')}",
    ]
    if repo.get("stars_gained"):
        lines.append(f"stars_this_week: {repo['stars_gained']}")
    if repo.get("updated"):
        lines.append(f"last_push: {repo['updated']}")
    content = "\n".join(lines)
    return f"[{idx}] " + wrap(repo["source"], content, uid=str(idx))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", default=None, help="GitHub Personal Access Token (read:public_repo)")
    parser.add_argument("--since", default="weekly", choices=["daily", "weekly", "monthly"])
    parser.add_argument("--filter-seen", action="store_true",
                        help="Exclut les repos déjà présentés dans un digest précédent")
    args = parser.parse_args()

    token = _read_token(args.token)
    results = {}

    # Load topics from config (fallback to legacy defaults)
    config_path = Path("~/.openclaw/config/github-watch/config.json").expanduser()
    topics = ["sysops", "devops"]  # legacy default
    if config_path.exists():
        try:
            cfg = json.loads(config_path.read_text(encoding="utf-8"))
            configured = cfg.get("topics")
            if isinstance(configured, list) and configured:
                topics = [t for t in configured if isinstance(t, str) and t.strip()]
        except Exception:
            pass

    # 1. Trending
    print(f"[*] GitHub Trending ({args.since})…", file=sys.stderr)
    try:
        trending = fetch_trending(since=args.since, token=token)
        print(f"[OK] Trending : {len(trending)} repos", file=sys.stderr)
    except Exception as e:
        print(f"[ERR] Trending : {e}", file=sys.stderr)
        trending = []
    results["trending"] = trending

    # 2. Topics (configurable via config.json)
    topic_repos = []
    for topic in topics:
        time.sleep(1)
        print(f"[*] GitHub topic:{topic}…", file=sys.stderr)
        try:
            repos = fetch_topic_repos(topic, per_page=25, token=token)
            print(f"[OK] {topic} : {len(repos)} repos", file=sys.stderr)
        except Exception as e:
            print(f"[ERR] {topic} : {e}", file=sys.stderr)
            repos = []
        results[topic] = repos
        topic_repos.extend(repos)

    # Filtre seen si demandé
    all_repos = trending + topic_repos
    skipped = 0
    if args.filter_seen:
        from seen_store import github_store
        all_repos, skipped = github_store.filter_unseen(all_repos, key_fn=lambda r: r["name"])
        print(f"[seen] {skipped} repos filtrés (déjà vus), {len(all_repos)} restants", file=sys.stderr)
        # Recalcule les listes filtrées pour cohérence dans results
        seen_names = {r["name"] for r in all_repos}
        results["trending"] = [r for r in trending if r["name"] in seen_names]
        for topic in topics:
            if topic in results:
                results[topic] = [r for r in results[topic] if r["name"] in seen_names]

    # Build wrapped listing
    header = build_prompt_header()
    wrapped = "\n\n".join(wrap_repo(r, i) for i, r in enumerate(all_repos))
    results["wrapped_listing"] = f"{header}\n\n{wrapped}"
    results["count"] = len(all_repos)
    results["skipped_seen"] = skipped

    # Use sys.stdout.buffer to avoid Windows cp1252 encoding issues
    out = json.dumps(results, ensure_ascii=False, indent=2)
    sys.stdout.buffer.write(out.encode("utf-8"))
    sys.stdout.buffer.write(b"\n")


if __name__ == "__main__":
    main()
