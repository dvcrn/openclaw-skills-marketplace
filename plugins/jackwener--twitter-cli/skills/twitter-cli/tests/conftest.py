from __future__ import annotations

from typing import Any

import pytest

from twitter_cli.models import Author, Metrics, Tweet


@pytest.fixture()
def tweet_factory():
    def _make_tweet(tweet_id: str = "1", **overrides: Any) -> Tweet:
        metrics = overrides.pop(
            "metrics",
            Metrics(likes=10, retweets=2, replies=1, quotes=0, views=120, bookmarks=3),
        )
        author = overrides.pop(
            "author",
            Author(id="u1", name="Alice", screen_name="alice", verified=False),
        )
        return Tweet(
            id=tweet_id,
            text=overrides.pop("text", "hello"),
            author=author,
            metrics=metrics,
            created_at=overrides.pop("created_at", "2025-01-01"),
            media=overrides.pop("media", []),
            urls=overrides.pop("urls", []),
            is_retweet=overrides.pop("is_retweet", False),
            lang=overrides.pop("lang", "en"),
            retweeted_by=overrides.pop("retweeted_by", None),
            quoted_tweet=overrides.pop("quoted_tweet", None),
            score=overrides.pop("score", 0.0),
        )

    return _make_tweet
