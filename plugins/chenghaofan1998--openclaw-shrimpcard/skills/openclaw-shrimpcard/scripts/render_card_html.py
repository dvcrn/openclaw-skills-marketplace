#!/usr/bin/env python3
import argparse
import base64
import json
from pathlib import Path


def _load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _svg_to_data_url(svg_path: Path) -> str:
    raw = svg_path.read_bytes()
    b64 = base64.b64encode(raw).decode("ascii")
    return "data:image/svg+xml;base64," + b64


def _to_card_data(card: dict, pixel_data_url: str) -> dict:
    card_id = card.get("card_id", "")
    if card_id and not card_id.startswith("ID:"):
        card_id = "ID:" + card_id

    tagline = card.get("tagline", "")
    description = card.get("description", "")
    if tagline and description:
        bio = tagline + "\n" + description
    else:
        bio = tagline or description

    owner = card.get("owner", {}) or {}
    footer = []
    if owner.get("name"):
        footer.append(f"DEPLOYED BY {owner.get('name')}")
    if owner.get("contact"):
        footer.append(owner.get("contact"))

    image_url = None
    image = card.get("image") or {}
    if isinstance(image, dict):
        image_url = image.get("data_url") or image.get("url")

    if not image_url:
        image_url = pixel_data_url

    qr_url = None
    qr = card.get("qr") or {}
    if isinstance(qr, dict):
        qr_url = qr.get("data_url") or qr.get("url")

    return {
        "card_id": card_id,
        "name": card.get("name", ""),
        "bio": bio,
        "skills": (card.get("top_skills") or [])[:3],
        "footer": footer,
        "image": image_url,
        "qr": qr_url,
    }


def _inject_data(template: str, card_data: dict) -> str:
    payload = json.dumps(card_data, ensure_ascii=False, indent=2)
    script = f"<script>\nwindow.__CARD_DATA__ = {payload};\n</script>\n"
    marker = "<!-- CARD_DATA -->"
    if marker in template:
        return template.replace(marker, script)
    return template.replace("</body>", script + "</body>")


def main():
    parser = argparse.ArgumentParser(description="Render ShrimpCard HTML from card JSON")
    parser.add_argument("card_json", help="Path to ShrimpCard JSON")
    parser.add_argument("--out", default="shrimp-card.html", help="Output HTML path")
    parser.add_argument(
        "--template",
        default=str(Path(__file__).resolve().parent.parent / "assets" / "card-template.html"),
        help="HTML template path",
    )
    parser.add_argument(
        "--pixel",
        default=str(Path(__file__).resolve().parent.parent / "assets" / "pixel-lobster.svg"),
        help="Pixel-art SVG path",
    )
    args = parser.parse_args()

    card_path = Path(args.card_json)
    template_path = Path(args.template)
    pixel_path = Path(args.pixel)

    card = _load_json(card_path)
    pixel_data_url = _svg_to_data_url(pixel_path)
    card_data = _to_card_data(card, pixel_data_url)

    template = template_path.read_text(encoding="utf-8")
    rendered = _inject_data(template, card_data)

    out_path = Path(args.out)
    out_path.write_text(rendered, encoding="utf-8")


if __name__ == "__main__":
    main()
