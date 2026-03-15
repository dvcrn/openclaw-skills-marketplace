# /// script
# requires-python = ">=3.13"
# dependencies = ["Pillow", "numpy"]
# ///
"""Remove Gemini AI watermark using Reverse Alpha Blending.

Based on: https://github.com/journey-ad/gemini-watermark-remover
Pure math approach — no AI inpainting, lossless restoration.
"""

import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image

SCRIPT_DIR = Path(__file__).parent
BG_48_PATH = SCRIPT_DIR / "bg_48.png"
BG_96_PATH = SCRIPT_DIR / "bg_96.png"

ALPHA_THRESHOLD = 0.002
MAX_ALPHA = 0.99
LOGO_VALUE = 255.0


def calculate_alpha_map(bg_path: Path, size: int) -> np.ndarray:
    """Calculate alpha map from watermark background capture image."""
    bg = Image.open(bg_path).convert("RGB").resize((size, size))
    bg_arr = np.array(bg, dtype=np.float32)
    # Max of RGB channels, normalized to [0, 1]
    return bg_arr.max(axis=2) / 255.0


def detect_watermark_config(width: int, height: int) -> dict:
    """Detect watermark size and position based on image dimensions."""
    if width > 1024 and height > 1024:
        logo_size, margin = 96, 64
    else:
        logo_size, margin = 48, 32
    return {
        "logo_size": logo_size,
        "x": width - margin - logo_size,
        "y": height - margin - logo_size,
    }


def remove_watermark(image_path: str, output_path: str) -> None:
    """Remove Gemini watermark from image."""
    img = Image.open(image_path).convert("RGB")
    width, height = img.size
    config = detect_watermark_config(width, height)
    logo_size = config["logo_size"]
    x, y = config["x"], config["y"]

    # Load alpha map
    bg_path = BG_96_PATH if logo_size == 96 else BG_48_PATH
    if not bg_path.exists():
        print(f"❌ Background image not found: {bg_path}", file=sys.stderr)
        sys.exit(1)
    alpha_map = calculate_alpha_map(bg_path, logo_size)

    # Convert to numpy array for processing
    img_arr = np.array(img, dtype=np.float32)

    # Extract watermark region
    region = img_arr[y : y + logo_size, x : x + logo_size, :3]

    # Apply reverse alpha blending
    alpha = alpha_map[:, :, np.newaxis]  # (H, W, 1) for broadcasting
    mask = alpha >= ALPHA_THRESHOLD
    alpha_clamped = np.clip(alpha, 0, MAX_ALPHA)
    one_minus_alpha = 1.0 - alpha_clamped

    # original = (watermarked - α × logo) / (1 - α)
    restored = np.where(
        mask,
        (region - alpha_clamped * LOGO_VALUE) / one_minus_alpha,
        region,
    )
    restored = np.clip(restored, 0, 255).astype(np.uint8)

    # Write back
    img_arr[y : y + logo_size, x : x + logo_size, :3] = restored
    result = Image.fromarray(img_arr.astype(np.uint8))
    result.save(output_path, quality=95)
    print(f"MEDIA:{output_path}")


def main():
    parser = argparse.ArgumentParser(description="Remove Gemini watermark from image")
    parser.add_argument("input", help="Input image path")
    parser.add_argument("-o", "--output", default=None, help="Output path (default: overwrites input)")
    args = parser.parse_args()

    output = args.output or args.input
    remove_watermark(args.input, output)


if __name__ == "__main__":
    main()
