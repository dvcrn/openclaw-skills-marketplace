"""Shared fixtures for xhs-cli tests."""

from __future__ import annotations

import pytest


@pytest.fixture
def tmp_config_dir(tmp_path, monkeypatch):
    """Override auth module's CONFIG_DIR to use a temp directory.

    Also disables browser cookie extraction to avoid subprocess calls.
    """
    import xhs_cli.auth as auth_module

    monkeypatch.setattr(auth_module, "CONFIG_DIR", tmp_path)
    monkeypatch.setattr(auth_module, "COOKIE_FILE", tmp_path / "cookies.json")
    monkeypatch.setattr(auth_module, "TOKEN_CACHE_FILE", tmp_path / "token_cache.json")
    # Prevent actual browser cookie extraction in tests
    monkeypatch.setattr(auth_module, "_extract_browser_cookies", lambda: None)
    return tmp_path


@pytest.fixture
def sample_cookie_str():
    return "a1=abc123; web_session=xyz789; webId=test_id"


@pytest.fixture
def sample_cookie_dict():
    return {"a1": "abc123", "web_session": "xyz789", "webId": "test_id"}
