"""Integration smoke tests — require a valid local saved login session.

These tests are marked with @pytest.mark.integration and are deselected by default.
Run explicitly with:

    uv run pytest tests/test_integration.py -v --override-ini="addopts="

By default, mutation tests are marked with @pytest.mark.live_mutation so they
can be excluded safely from day-to-day smoke runs.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time

import pytest
from click.testing import CliRunner

from xhs_cli.cli import cli

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def runner():
    return CliRunner()


def _run_cli(*args: str, timeout: int = 90) -> subprocess.CompletedProcess:
    """Run xhs command via subprocess to avoid event loop conflicts."""
    return subprocess.run(
        [sys.executable, "-m", "xhs_cli.cli", *args],
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def _run_cli_json(*args: str, timeout: int = 90):
    """Run command and parse JSON output."""
    result = _run_cli(*args, timeout=timeout)
    assert result.returncode == 0, (
        f"command failed: {' '.join(args)}\n{result.stdout}{result.stderr}"
    )
    return json.loads(result.stdout)


def _extract_user_id(data: dict) -> str:
    """Extract user_id from whoami JSON output."""
    for sub_key in ["userInfo", "basicInfo", "basic_info"]:
        sub = data.get(sub_key, {})
        if isinstance(sub, dict):
            uid = sub.get("userId", "") or sub.get("user_id", "")
            if uid:
                return str(uid)
    return str(data.get("userId", "") or data.get("user_id", "") or data.get("id", ""))


def _extract_note_from_search_items(items: list[dict]) -> dict[str, str]:
    """Pick one note_id/xsec_token pair from search/feed style items."""
    for item in items:
        if not isinstance(item, dict):
            continue
        note_id = str(item.get("id", "") or item.get("noteId", "") or item.get("note_id", ""))
        xsec_token = str(item.get("xsec_token", "") or item.get("xsecToken", ""))
        if note_id:
            return {"note_id": note_id, "xsec_token": xsec_token}
    return {"note_id": "", "xsec_token": ""}


def _note_cli_args(note: dict[str, str]) -> list[str]:
    args = [note["note_id"]]
    token = note.get("xsec_token", "")
    if token:
        args.extend(["--xsec-token", token])
    return args


def _find_note_id_by_title(user_id: str, title: str) -> str:
    """Find a recently posted note_id from user-posts JSON output by title."""
    posts = _run_cli_json("user-posts", user_id, "--json", timeout=120)
    if not isinstance(posts, list):
        return ""
    for item in posts:
        if not isinstance(item, dict):
            continue
        note_card = item.get("note_card", item.get("noteCard", item))
        if not isinstance(note_card, dict):
            note_card = item
        note_title = str(
            note_card.get("display_title", "")
            or note_card.get("displayTitle", "")
            or note_card.get("title", "")
        )
        if title and title in note_title:
            return str(item.get("id", "") or item.get("noteId", "") or item.get("note_id", ""))
    return ""


@pytest.fixture(scope="module")
def user_id() -> str:
    whoami_data = _run_cli_json("whoami", "--json")
    uid = _extract_user_id(whoami_data)
    if not uid:
        pytest.skip("Cannot extract user_id from whoami")
    return uid


@pytest.fixture(scope="module")
def sample_note() -> dict[str, str]:
    search_items = _run_cli_json("search", "咖啡", "--json", timeout=120)
    if isinstance(search_items, list):
        note = _extract_note_from_search_items(search_items)
        if note["note_id"]:
            return note

    feed_items = _run_cli_json("feed", "--json", timeout=120)
    if isinstance(feed_items, list):
        note = _extract_note_from_search_items(feed_items)
        if note["note_id"]:
            return note

    pytest.skip("No note_id available from search/feed")


# ===== Auth =====


class TestAuth:
    def test_status(self, runner):
        result = runner.invoke(cli, ["status"])
        assert result.exit_code == 0
        assert "Logged in" in result.output

    def test_whoami(self):
        result = _run_cli("whoami")
        assert result.returncode == 0, f"whoami failed: {result.stdout}{result.stderr}"

    def test_whoami_json(self):
        data = _run_cli_json("whoami", "--json")
        assert isinstance(data, dict)


# ===== Search / Read =====


class TestSearchAndRead:
    def test_search(self, runner):
        result = runner.invoke(cli, ["search", "咖啡"])
        assert result.exit_code == 0

    def test_search_json(self):
        data = _run_cli_json("search", "咖啡", "--json", timeout=120)
        assert isinstance(data, list)

    def test_read(self, sample_note):
        result = _run_cli("read", *_note_cli_args(sample_note), timeout=120)
        assert result.returncode == 0, f"read failed: {result.stdout}{result.stderr}"

    def test_read_json_with_comments(self, sample_note):
        args = ["read", *_note_cli_args(sample_note), "--comments", "--json"]
        data = _run_cli_json(*args, timeout=120)
        assert isinstance(data, dict)
        assert "note" in data


# ===== Feed / Topics =====


class TestDiscovery:
    def test_feed(self, runner):
        result = runner.invoke(cli, ["feed"])
        assert result.exit_code == 0

    def test_feed_json(self):
        data = _run_cli_json("feed", "--json", timeout=120)
        assert isinstance(data, list)

    def test_topics(self, runner):
        result = runner.invoke(cli, ["topics", "旅行"])
        assert result.exit_code == 0

    def test_topics_json(self):
        data = _run_cli_json("topics", "旅行", "--json", timeout=120)
        assert isinstance(data, list)


# ===== User =====


class TestUser:
    def test_user(self, user_id):
        result = _run_cli("user", user_id, timeout=120)
        assert result.returncode == 0, f"user failed: {result.stdout}{result.stderr}"

    def test_user_posts(self, user_id):
        result = _run_cli("user-posts", user_id, timeout=120)
        assert result.returncode == 0, f"user-posts failed: {result.stdout}{result.stderr}"

    def test_followers_json(self, user_id):
        data = _run_cli_json("followers", user_id, "--json", timeout=120)
        assert isinstance(data, list)

    def test_following_json(self, user_id):
        data = _run_cli_json("following", user_id, "--json", timeout=120)
        assert isinstance(data, list)


# ===== Favorites =====


class TestFavorites:
    def test_favorites(self, user_id):
        result = _run_cli("favorites", "--max", "3", timeout=120)
        assert result.returncode == 0, f"favorites failed: {result.stdout}{result.stderr}"

    def test_favorites_json(self, user_id):
        data = _run_cli_json("favorites", "--max", "3", "--json", timeout=120)
        assert isinstance(data, list)


# ===== Optional mutation smoke =====


@pytest.mark.live_mutation
class TestMutation:
    def test_like_then_unlike(self, sample_note):
        result = _run_cli("like", *_note_cli_args(sample_note), timeout=120)
        assert result.returncode == 0, f"like failed: {result.stdout}{result.stderr}"

        result = _run_cli("unlike", *_note_cli_args(sample_note), timeout=120)
        assert result.returncode == 0, f"unlike failed: {result.stdout}{result.stderr}"

    def test_favorite_then_unfavorite(self, sample_note):
        result = _run_cli("favorite", *_note_cli_args(sample_note), timeout=120)
        assert result.returncode == 0, f"favorite failed: {result.stdout}{result.stderr}"

        result = _run_cli("unfavorite", *_note_cli_args(sample_note), timeout=120)
        assert result.returncode == 0, f"unfavorite failed: {result.stdout}{result.stderr}"

    def test_comment_optional(self, sample_note):
        text = os.getenv("XHS_SMOKE_COMMENT_TEXT", "").strip()
        if not text:
            pytest.skip("XHS_SMOKE_COMMENT_TEXT not set; skip comment smoke")

        args = ["comment", *_note_cli_args(sample_note), text]
        result = _run_cli(*args, timeout=120)
        assert result.returncode == 0, f"comment failed: {result.stdout}{result.stderr}"

    def test_post_optional(self):
        title_prefix = os.getenv("XHS_SMOKE_POST_TITLE", "Smoke test post").strip()
        title = f"{title_prefix} {int(time.time())}"
        content = os.getenv("XHS_SMOKE_POST_CONTENT", "posted by smoke test").strip()
        images_raw = os.getenv("XHS_SMOKE_POST_IMAGES", "").strip()

        if not images_raw:
            pytest.skip("XHS_SMOKE_POST_IMAGES not set; skip post smoke")

        image_paths = [p.strip() for p in images_raw.split(",") if p.strip()]
        if not image_paths:
            pytest.skip("No usable image path in XHS_SMOKE_POST_IMAGES")

        args = ["post", title]
        for path in image_paths:
            args.extend(["--image", path])
        if content:
            args.extend(["--content", content])
        args.append("--json")

        result = _run_cli(*args, timeout=180)
        combined_output = f"{result.stdout}{result.stderr}"
        if result.returncode != 0 and "Creator platform login required" in combined_output:
            pytest.skip("creator platform login is not available in current local session")
        assert result.returncode == 0, f"post failed: {result.stdout}{result.stderr}"
        payload = json.loads(result.stdout)
        assert payload.get("success") is True

        note_id = str(payload.get("note_id", ""))
        if not note_id:
            user_id = _extract_user_id(_run_cli_json("whoami", "--json", timeout=120))
            if user_id:
                note_id = _find_note_id_by_title(user_id, title)
        assert note_id, "post succeeded but note_id could not be resolved"

        delete_result = _run_cli("delete", note_id, timeout=120)
        assert delete_result.returncode == 0, (
            f"delete failed: {delete_result.stdout}{delete_result.stderr}"
        )
