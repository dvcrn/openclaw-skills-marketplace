#!/usr/bin/env python3
"""Poe Connector — Image, video, and audio generation via Poe media models."""

import argparse
import base64
import re
import sys
import os
import urllib.request
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

from poe_utils import get_client, retry_on_rate_limit, handle_api_error, parse_extra_body, get_default_model
import openai

FALLBACK_MODELS = {
    "image": "GPT-Image-1",
    "video": "Veo-3",
    "audio": "ElevenLabs",
}

DEFAULT_EXTENSIONS = {
    "image": ".png",
    "video": ".mp4",
    "audio": ".mp3",
}


def extract_and_save_media(content: str, output_path: str | None, media_type: str) -> str | None:
    """Try to find a base64 data URL or a regular URL in the response content and save/report it."""
    data_url_match = re.search(r"data:([^;]+);base64,([A-Za-z0-9+/=]+)", content)
    if data_url_match:
        mime, b64_data = data_url_match.group(1), data_url_match.group(2)
        raw = base64.b64decode(b64_data)
        if not output_path:
            ext = DEFAULT_EXTENSIONS.get(media_type, ".bin")
            output_path = f"poe_generated_{media_type}{ext}"
        Path(output_path).write_bytes(raw)
        print(f"Saved {media_type} to: {output_path}")
        return output_path

    url_match = re.search(r"https?://\S+", content)
    if url_match:
        url = url_match.group(0).rstrip(")")
        if output_path:
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 poe-connector/1.0"})
                with urllib.request.urlopen(req) as resp:
                    Path(output_path).write_bytes(resp.read())
                print(f"Saved {media_type} to: {output_path}")
                print(f"Source URL: {url}")
            except Exception as e:
                print(f"Generated {media_type} URL: {url}")
                print(f"Warning: failed to download — {e}", file=sys.stderr)
        else:
            print(f"Generated {media_type} URL: {url}")
        return output_path or url

    return None


def generate_media(
    model: str,
    prompt: str,
    media_type: str,
    output: str | None = None,
    extra_body: dict | None = None,
) -> None:
    """Send a media generation request to Poe and handle the response."""
    client = get_client()

    kwargs: dict = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
    }
    if extra_body:
        kwargs["extra_body"] = extra_body

    def do_generate():
        return client.chat.completions.create(**kwargs)

    try:
        response = retry_on_rate_limit(do_generate)
    except openai.APIError as e:
        handle_api_error(e)
        sys.exit(1)

    content = response.choices[0].message.content
    if not content:
        print("Error: Empty response from model.", file=sys.stderr)
        sys.exit(1)

    saved = extract_and_save_media(content, output, media_type)
    if not saved:
        print(content)

    usage = response.usage
    if usage:
        print(
            f"\n--- Usage: {usage.prompt_tokens} prompt + "
            f"{usage.completion_tokens} completion = "
            f"{usage.total_tokens} total tokens ---",
            file=sys.stderr,
        )


def main():
    parser = argparse.ArgumentParser(
        description="Generate images, videos, and audio via Poe media models.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            '  %(prog)s --type image --prompt "A sunset over mountains"\n'
            '  %(prog)s --type image --model Imagen-4 --prompt "Cyberpunk city" --aspect 16:9\n'
            '  %(prog)s --type video --model Veo-3 --prompt "A cat playing piano"\n'
            '  %(prog)s --type audio --model ElevenLabs --prompt "Hello world"\n'
        ),
    )
    parser.add_argument(
        "--type", "-t",
        required=True,
        choices=["image", "video", "audio"],
        help="Media type to generate",
    )
    parser.add_argument("--model", "-m", help="Poe model name (defaults vary by type)")
    parser.add_argument("--prompt", "-p", required=True, help="Generation prompt / text")
    parser.add_argument("--output", "-o", help="Output file path (auto-named if omitted)")
    parser.add_argument("--aspect", help='Aspect ratio for image models (e.g. "1:1", "3:2", "16:9")')
    parser.add_argument("--quality", help='Quality level for image models (e.g. "low", "medium", "high")')
    parser.add_argument("--extra", help='Additional params as JSON (e.g. \'{"duration": 5}\')')

    args = parser.parse_args()
    model = args.model or get_default_model(args.type) or FALLBACK_MODELS.get(args.type, "GPT-Image-1")

    extra = parse_extra_body(args.extra) or {}
    if args.aspect:
        extra["aspect"] = args.aspect
    if args.quality:
        extra["quality"] = args.quality

    generate_media(
        model=model,
        prompt=args.prompt,
        media_type=args.type,
        output=args.output,
        extra_body=extra or None,
    )


if __name__ == "__main__":
    main()
