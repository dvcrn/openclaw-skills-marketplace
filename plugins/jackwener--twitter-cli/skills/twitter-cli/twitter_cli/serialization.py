"""Serialization helpers for Tweet models."""

from __future__ import annotations

import json
from typing import Any, Dict, Iterable, List, Optional

from .models import Author, Metrics, Tweet, TweetMedia


def tweet_to_dict(tweet: Tweet) -> Dict[str, Any]:
    """Convert a Tweet dataclass into a JSON-safe dict."""
    data = {
        "id": tweet.id,
        "text": tweet.text,
        "author": {
            "id": tweet.author.id,
            "name": tweet.author.name,
            "screenName": tweet.author.screen_name,
            "profileImageUrl": tweet.author.profile_image_url,
            "verified": tweet.author.verified,
        },
        "metrics": {
            "likes": tweet.metrics.likes,
            "retweets": tweet.metrics.retweets,
            "replies": tweet.metrics.replies,
            "quotes": tweet.metrics.quotes,
            "views": tweet.metrics.views,
            "bookmarks": tweet.metrics.bookmarks,
        },
        "createdAt": tweet.created_at,
        "media": [
            {
                "type": media.type,
                "url": media.url,
                "width": media.width,
                "height": media.height,
            }
            for media in tweet.media
        ],
        "urls": list(tweet.urls),
        "isRetweet": tweet.is_retweet,
        "retweetedBy": tweet.retweeted_by,
        "lang": tweet.lang,
        "score": tweet.score,
    }
    if tweet.quoted_tweet:
        data["quotedTweet"] = {
            "id": tweet.quoted_tweet.id,
            "text": tweet.quoted_tweet.text,
            "author": {
                "screenName": tweet.quoted_tweet.author.screen_name,
                "name": tweet.quoted_tweet.author.name,
            },
        }
    return data


def tweet_from_dict(data: Dict[str, Any]) -> Tweet:
    """Convert a dict into a Tweet dataclass."""
    author_data = data.get("author") or {}
    metrics_data = data.get("metrics") or {}
    media_data = data.get("media") or []
    quoted_data = data.get("quotedTweet")

    quoted_tweet = None  # type: Optional[Tweet]
    if isinstance(quoted_data, dict):
        quoted_author = quoted_data.get("author") or {}
        quoted_tweet = Tweet(
            id=str(quoted_data.get("id") or ""),
            text=str(quoted_data.get("text") or ""),
            author=Author(
                id="",
                name=str(quoted_author.get("name") or ""),
                screen_name=str(quoted_author.get("screenName") or ""),
            ),
            metrics=Metrics(),
            created_at="",
        )

    return Tweet(
        id=str(data.get("id") or ""),
        text=str(data.get("text") or ""),
        author=Author(
            id=str(author_data.get("id") or ""),
            name=str(author_data.get("name") or ""),
            screen_name=str(author_data.get("screenName") or ""),
            profile_image_url=str(author_data.get("profileImageUrl") or ""),
            verified=bool(author_data.get("verified", False)),
        ),
        metrics=Metrics(
            likes=int(metrics_data.get("likes") or 0),
            retweets=int(metrics_data.get("retweets") or 0),
            replies=int(metrics_data.get("replies") or 0),
            quotes=int(metrics_data.get("quotes") or 0),
            views=int(metrics_data.get("views") or 0),
            bookmarks=int(metrics_data.get("bookmarks") or 0),
        ),
        created_at=str(data.get("createdAt") or ""),
        media=[
            TweetMedia(
                type=str(item.get("type") or ""),
                url=str(item.get("url") or ""),
                width=_optional_int(item.get("width")),
                height=_optional_int(item.get("height")),
            )
            for item in media_data
            if isinstance(item, dict)
        ],
        urls=[str(url) for url in (data.get("urls") or [])],
        is_retweet=bool(data.get("isRetweet", False)),
        lang=str(data.get("lang") or ""),
        retweeted_by=_optional_str(data.get("retweetedBy")),
        quoted_tweet=quoted_tweet,
        score=float(data.get("score") or 0.0),
    )


def tweets_from_json(raw: str) -> List[Tweet]:
    """Parse a JSON string into Tweet objects."""
    payload = json.loads(raw)
    if not isinstance(payload, list):
        raise ValueError("Tweet JSON payload must be a list")
    return [tweet_from_dict(item) for item in payload if isinstance(item, dict)]


def tweets_to_json(tweets: Iterable[Tweet]) -> str:
    """Serialize Tweet objects to pretty JSON."""
    return json.dumps([tweet_to_dict(tweet) for tweet in tweets], ensure_ascii=False, indent=2)


def _optional_int(value: Any) -> Optional[int]:
    """Parse an optional integer value."""
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _optional_str(value: Any) -> Optional[str]:
    """Parse an optional string value."""
    if value is None:
        return None
    text = str(value)
    return text if text else None
