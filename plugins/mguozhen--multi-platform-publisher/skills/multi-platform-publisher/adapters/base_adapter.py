"""
Base adapter interface for social media platforms.
All platform adapters must inherit from ``BaseAdapter`` and implement
the abstract methods defined here.
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseAdapter(ABC):
    """Abstract base class for every social-media platform adapter."""

    # Subclasses MUST override these class-level attributes.
    DISPLAY_NAME: str = "Unknown"
    AUTH_METHOD: str = "Unknown"
    FEATURES: list[str] = []
    MAX_TEXT_LENGTH: int = 0
    MAX_IMAGES: int = 0

    def __init__(self, config: dict):
        self.config = config

    # ------------------------------------------------------------------
    # Abstract interface
    # ------------------------------------------------------------------
    @abstractmethod
    def publish(self, content: Any, images: list[str] | None = None) -> dict:
        """Publish *content* (already adapted) to the platform.

        Parameters
        ----------
        content : Any
            Platform-specific content payload (string, list of strings for
            threads, HTML string, etc.).
        images : list[str] | None
            Paths to processed image files.

        Returns
        -------
        dict
            ``{"success": bool, "message": str, "url": str | None, "error": str | None}``
        """

    @abstractmethod
    def validate(self) -> bool:
        """Return ``True`` if the stored credentials are valid."""

    @abstractmethod
    def upload_image(self, image_path: str) -> str | None:
        """Upload an image and return a platform-specific media identifier
        (media_id, asset URN, media_id on WeChat, etc.).  Return ``None``
        on failure."""

    # ------------------------------------------------------------------
    # Helpers available to all adapters
    # ------------------------------------------------------------------
    @staticmethod
    def _env(key: str, default: str = "") -> str:
        """Read an environment variable with a fallback."""
        return os.environ.get(key, default)


import os  # noqa: E402 – placed after class body for readability
