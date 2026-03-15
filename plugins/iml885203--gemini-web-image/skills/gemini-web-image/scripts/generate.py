# /// script
# requires-python = ">=3.13"
# dependencies = ["gemini-webapi>=1.19", "browser-cookie3", "Pillow", "numpy"]
# ///
"""Generate or edit images using Gemini Web API (Google AI Pro subscription).

Uses browser-cookie3 to read cookies from Chrome automatically.
Falls back to ~/.config/gemini/cookies.json if browser cookies unavailable.
"""

import argparse
import asyncio
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from gemini_webapi import GeminiClient
from gemini_webapi.constants import Model

SCRIPT_DIR = Path(__file__).parent


def _remove_watermark(image_path: str) -> None:
    """Remove Gemini watermark in-place using reverse alpha blending."""
    try:
        import numpy as np
        from PIL import Image

        bg_48 = SCRIPT_DIR / "bg_48.png"
        bg_96 = SCRIPT_DIR / "bg_96.png"

        img = Image.open(image_path).convert("RGB")
        w, h = img.size

        if w > 1024 and h > 1024:
            logo_size, margin, bg_path = 96, 64, bg_96
        else:
            logo_size, margin, bg_path = 48, 32, bg_48

        if not bg_path.exists():
            return  # Skip silently if assets missing

        # Alpha map from background capture
        bg = Image.open(bg_path).convert("RGB").resize((logo_size, logo_size))
        alpha_map = np.array(bg, dtype=np.float32).max(axis=2) / 255.0

        x = w - margin - logo_size
        y = h - margin - logo_size
        img_arr = np.array(img, dtype=np.float32)
        region = img_arr[y:y + logo_size, x:x + logo_size, :3]

        alpha = alpha_map[:, :, np.newaxis]
        mask = alpha >= 0.002
        alpha_c = np.clip(alpha, 0, 0.99)

        restored = np.where(mask, (region - alpha_c * 255.0) / (1.0 - alpha_c), region)
        img_arr[y:y + logo_size, x:x + logo_size, :3] = np.clip(restored, 0, 255)

        Image.fromarray(img_arr.astype(np.uint8)).save(image_path, quality=95)
    except Exception:
        pass  # Don't fail the whole pipeline if watermark removal fails

COOKIE_PATH = Path.home() / ".config" / "gemini" / "cookies.json"


def make_client() -> GeminiClient:
    """Create client: try browser cookies first, fall back to manual cookies."""
    if COOKIE_PATH.exists():
        cookies = json.loads(COOKIE_PATH.read_text())
        if cookies.get("secure_1psid"):
            return GeminiClient(
                secure_1psid=cookies["secure_1psid"],
                secure_1psidts=cookies.get("secure_1psidts", ""),
            )
    # No manual cookies → let browser-cookie3 handle it
    return GeminiClient()


async def generate(prompt: str, output: str, input_image: str | None = None, delete_chat: bool = True) -> None:
    client = make_client()
    await client.init(auto_close=False, auto_refresh=False, timeout=90)

    if input_image:
        response = await asyncio.wait_for(
            client.generate_content(prompt, files=[input_image], model=Model.G_3_0_FLASH),
            timeout=120,
        )
    else:
        response = await asyncio.wait_for(
            client.generate_content(prompt, model=Model.G_3_0_FLASH),
            timeout=180,
        )

    chat_id = response.metadata[0] if getattr(response, "metadata", None) else None

    if response.images:
        img = response.images[0]
        output_path = Path(output)

        # gemini-webapi's save() creates a directory; handle that
        tmp_dir = output_path.with_name(f"_tmp_{output_path.stem}")
        await img.save(str(tmp_dir))

        if tmp_dir.is_dir():
            files = list(tmp_dir.glob("*"))
            if files:
                actual = files[0]
                final = output_path.with_suffix(actual.suffix)
                actual.rename(final)
                for f in tmp_dir.iterdir():
                    f.unlink()
                tmp_dir.rmdir()
                # Auto-remove watermark
                _remove_watermark(str(final))
                print(f"MEDIA:{final}")
            else:
                print("❌ No image file in output directory", file=sys.stderr)
                tmp_dir.rmdir()
        elif tmp_dir.is_file():
            tmp_dir.rename(output_path)
            _remove_watermark(str(output_path))
            print(f"MEDIA:{output_path}")

        if delete_chat and chat_id:
            try:
                await client.delete_chat(chat_id)
            except Exception:
                pass
    else:
        if delete_chat and chat_id:
            try:
                await client.delete_chat(chat_id)
            except Exception:
                pass
        if response.text:
            print(response.text)
        else:
            print("❌ No images generated", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Generate images via Gemini Web API")
    parser.add_argument("--prompt", "-p", required=True, help="Image prompt")
    parser.add_argument("--output", "-o", default=None, help="Output filename")
    parser.add_argument("--input", "-i", default=None, help="Input image for editing")
    parser.add_argument("--keep-chat", action="store_true", help="Keep Gemini conversation history (default: delete chat after generation)")
    args = parser.parse_args()

    if args.output is None:
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        args.output = f"{ts}-generated.png"

    asyncio.run(generate(args.prompt, args.output, args.input, delete_chat=not args.keep_chat))



if __name__ == "__main__":
    main()
