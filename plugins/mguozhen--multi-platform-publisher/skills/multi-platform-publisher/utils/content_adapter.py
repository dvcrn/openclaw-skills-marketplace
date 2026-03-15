"""
Content Adapter
===============
Transforms raw article / post content into platform-specific formats.

Each platform has different constraints (character limits, formatting
rules, tone expectations).  ``ContentAdapter`` applies the right
transformation based on the target platform key.
"""

from __future__ import annotations

import re
import textwrap
from typing import Any


class ContentAdapter:
    """Adapt a single piece of content for multiple social-media platforms."""

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------
    def adapt(self, content: str, platform: str, *, as_thread: bool = False) -> Any:
        """Return *content* transformed for *platform*.

        Parameters
        ----------
        content : str
            Raw Markdown / plain-text content.
        platform : str
            Target platform key (``twitter``, ``linkedin``, ``wechat``,
            ``xiaohongshu``).
        as_thread : bool
            For Twitter – split into a thread instead of truncating.

        Returns
        -------
        Any
            Platform-specific payload.  May be ``str``, ``list[str]``, or
            ``dict`` depending on the platform.
        """
        method = getattr(self, f"_adapt_{platform}", None)
        if method is None:
            return content
        return method(content, as_thread=as_thread)

    # ==================================================================
    # Twitter / X
    # ==================================================================
    def _adapt_twitter(self, content: str, *, as_thread: bool = False) -> str | list[str]:
        """Adapt content for X / Twitter (max 280 chars per tweet)."""
        clean = self._strip_markdown(content).strip()
        hashtags = self._extract_hashtags(content)
        suffix = (" " + " ".join(hashtags)) if hashtags else ""

        if as_thread or len(clean + suffix) > 280:
            return self._split_thread(clean, hashtags)

        return (clean + suffix)[:280]

    def _split_thread(self, text: str, hashtags: list[str], max_len: int = 270) -> list[str]:
        """Split *text* into a list of tweets suitable for a thread.

        Strategy: split on sentence boundaries, then pack sentences into
        tweets without exceeding *max_len* (leaving room for numbering).
        """
        sentences = re.split(r"(?<=[.!?。！？])\s+", text)
        tweets: list[str] = []
        current = ""

        for sentence in sentences:
            if len(current) + len(sentence) + 1 <= max_len:
                current = f"{current} {sentence}".strip() if current else sentence
            else:
                if current:
                    tweets.append(current)
                # If a single sentence exceeds max_len, hard-wrap it.
                if len(sentence) > max_len:
                    for chunk in textwrap.wrap(sentence, max_len):
                        tweets.append(chunk)
                else:
                    current = sentence
                    continue
                current = ""
        if current:
            tweets.append(current)

        # Add numbering and hashtags to the last tweet
        total = len(tweets)
        if total > 1:
            tweets = [f"{i + 1}/{total} {t}" for i, t in enumerate(tweets)]
        if hashtags:
            tag_str = " ".join(hashtags)
            last = tweets[-1]
            if len(last) + len(tag_str) + 1 <= 280:
                tweets[-1] = f"{last} {tag_str}"
            else:
                tweets.append(tag_str)

        return tweets

    # ==================================================================
    # LinkedIn
    # ==================================================================
    def _adapt_linkedin(self, content: str, **_: Any) -> str:
        """Adapt content for LinkedIn (professional tone, up to 3 000 chars)."""
        clean = self._strip_markdown(content)
        # Add line breaks for readability
        paragraphs = [p.strip() for p in clean.split("\n\n") if p.strip()]
        formatted = "\n\n".join(paragraphs)

        hashtags = self._extract_hashtags(content)
        if hashtags:
            formatted += "\n\n" + " ".join(hashtags)

        return formatted[:3000]

    # ==================================================================
    # WeChat Official Account
    # ==================================================================
    def _adapt_wechat(self, content: str, **_: Any) -> dict:
        """Adapt content for WeChat Official Account.

        Returns a dict with ``title``, ``content`` (HTML), ``digest``,
        and ``author``.
        """
        title = self._extract_title(content)
        html_body = self._markdown_to_html(content)
        digest = self._generate_digest(content, max_len=120)

        return {
            "title": title,
            "content": html_body,
            "digest": digest,
            "author": "",
        }

    # ==================================================================
    # Xiaohongshu (小红书)
    # ==================================================================
    def _adapt_xiaohongshu(self, content: str, **_: Any) -> dict:
        """Adapt content for Xiaohongshu (casual, emoji-rich, ≤1 000 chars)."""
        clean = self._strip_markdown(content)
        title = self._extract_title(content)[:20]

        # Add emoji flair
        desc = self._add_xhs_emoji(clean)

        # Add topic tags
        tags = self._extract_hashtags(content)
        if tags:
            tag_line = " ".join(f"#{t.lstrip('#')}" for t in tags)
            desc = f"{desc}\n\n{tag_line}"

        return {
            "title": title,
            "desc": desc[:1000],
        }

    # ==================================================================
    # Shared helpers
    # ==================================================================
    @staticmethod
    def _strip_markdown(text: str) -> str:
        """Remove common Markdown syntax, keeping plain text."""
        text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)  # headings
        text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)  # bold
        text = re.sub(r"\*(.+?)\*", r"\1", text)  # italic
        text = re.sub(r"`(.+?)`", r"\1", text)  # inline code
        text = re.sub(r"!\[.*?\]\(.*?\)", "", text)  # images
        text = re.sub(r"\[(.+?)\]\(.*?\)", r"\1", text)  # links → text
        text = re.sub(r"^[-*+]\s+", "• ", text, flags=re.MULTILINE)  # lists
        text = re.sub(r"^>\s+", "", text, flags=re.MULTILINE)  # blockquotes
        text = re.sub(r"---+", "", text)  # horizontal rules
        return text.strip()

    @staticmethod
    def _extract_title(content: str) -> str:
        """Extract the first heading or first line as a title."""
        match = re.search(r"^#{1,6}\s+(.+)$", content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        first_line = content.strip().split("\n")[0]
        return first_line[:60]

    @staticmethod
    def _extract_hashtags(content: str) -> list[str]:
        """Extract hashtags from content (``#tag`` patterns)."""
        tags = re.findall(r"(?:^|\s)(#\w+)", content)
        return list(dict.fromkeys(tags))[:5]  # deduplicate, max 5

    @staticmethod
    def _generate_digest(content: str, max_len: int = 120) -> str:
        """Generate a short digest / summary from the first paragraph."""
        clean = re.sub(r"^#{1,6}\s+.+$", "", content, flags=re.MULTILINE).strip()
        first_para = clean.split("\n\n")[0] if "\n\n" in clean else clean
        first_para = re.sub(r"\s+", " ", first_para).strip()
        if len(first_para) > max_len:
            return first_para[: max_len - 3] + "..."
        return first_para

    @staticmethod
    def _markdown_to_html(content: str) -> str:
        """Minimal Markdown → HTML conversion for WeChat articles.

        For production use, consider a full Markdown parser such as
        ``markdown`` or ``mistune``.
        """
        html = content

        # Headings
        for level in range(6, 0, -1):
            pattern = re.compile(rf"^{'#' * level}\s+(.+)$", re.MULTILINE)
            html = pattern.sub(rf"<h{level}>\1</h{level}>", html)

        # Bold / italic
        html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)
        html = re.sub(r"\*(.+?)\*", r"<em>\1</em>", html)

        # Inline code
        html = re.sub(r"`(.+?)`", r"<code>\1</code>", html)

        # Links
        html = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', html)

        # Images
        html = re.sub(r"!\[(.+?)\]\((.+?)\)", r'<img src="\2" alt="\1" />', html)

        # Paragraphs (double newline)
        paragraphs = html.split("\n\n")
        wrapped = []
        for p in paragraphs:
            p = p.strip()
            if p and not p.startswith("<h") and not p.startswith("<img"):
                p = f"<p>{p}</p>"
            wrapped.append(p)
        html = "\n".join(wrapped)

        # Line breaks
        html = html.replace("\n", "<br/>\n")

        # Wrap in a styled section for WeChat
        return (
            '<section style="font-size:16px;line-height:1.8;color:#333;">'
            f"{html}"
            "</section>"
        )

    @staticmethod
    def _add_xhs_emoji(text: str) -> str:
        """Sprinkle emoji into text for Xiaohongshu's casual style."""
        emoji_map = {
            "推荐": "💯 推荐",
            "分享": "📢 分享",
            "总结": "📝 总结",
            "注意": "⚠️ 注意",
            "技巧": "💡 技巧",
            "经验": "✨ 经验",
            "recommend": "💯 recommend",
            "share": "📢 share",
            "summary": "📝 summary",
            "tips": "💡 tips",
        }
        for word, replacement in emoji_map.items():
            text = text.replace(word, replacement)
        return text
