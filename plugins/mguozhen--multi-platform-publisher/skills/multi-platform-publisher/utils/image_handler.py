"""
Image Handler
=============
Validates, resizes, and converts images before uploading to social
media platforms.  Each platform has its own size / format constraints;
this module normalises images to a common baseline.
"""

from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

# Pillow is an optional dependency – degrade gracefully.
try:
    from PIL import Image

    HAS_PIL = True
except ImportError:
    HAS_PIL = False


class ImageHandler:
    """Pre-process images for multi-platform publishing."""

    # Sensible defaults that satisfy most platforms.
    MAX_WIDTH = 4096
    MAX_HEIGHT = 4096
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
    ALLOWED_FORMATS = {"JPEG", "PNG", "GIF", "WEBP"}

    def __init__(self, temp_dir: str | None = None):
        self.temp_dir = temp_dir or tempfile.mkdtemp(prefix="mpp_images_")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def process_images(self, paths: list[str]) -> list[str]:
        """Validate and process a list of image paths.

        Returns a list of paths to processed images (may be the originals
        if no transformation was needed).
        """
        processed: list[str] = []
        for p in paths:
            result = self.process_image(p)
            if result:
                processed.append(result)
        return processed

    def process_image(self, image_path: str) -> str | None:
        """Process a single image.  Returns the (possibly new) path or
        ``None`` if the file is invalid."""
        path = Path(image_path)
        if not path.exists():
            return None

        if not HAS_PIL:
            # Without Pillow we can only do basic checks.
            if path.stat().st_size > self.MAX_FILE_SIZE:
                return None
            return str(path)

        try:
            img = Image.open(path)
        except Exception:
            return None

        if img.format and img.format.upper() not in self.ALLOWED_FORMATS:
            img = img.convert("RGB")

        # Resize if necessary
        if img.width > self.MAX_WIDTH or img.height > self.MAX_HEIGHT:
            img.thumbnail((self.MAX_WIDTH, self.MAX_HEIGHT), Image.LANCZOS)

        # Check file size – re-encode with quality reduction if needed
        out_path = Path(self.temp_dir) / f"{path.stem}_processed.jpg"
        quality = 95
        while quality >= 30:
            img.save(out_path, format="JPEG", quality=quality, optimize=True)
            if out_path.stat().st_size <= self.MAX_FILE_SIZE:
                return str(out_path)
            quality -= 10

        return None

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def get_image_info(image_path: str) -> dict[str, Any] | None:
        """Return basic metadata about an image."""
        if not HAS_PIL:
            return {"path": image_path, "size": os.path.getsize(image_path)}
        try:
            img = Image.open(image_path)
            return {
                "path": image_path,
                "width": img.width,
                "height": img.height,
                "format": img.format,
                "size": os.path.getsize(image_path),
            }
        except Exception:
            return None

    def cleanup(self) -> None:
        """Remove the temporary directory and all processed images."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
