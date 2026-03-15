#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "ultralytics>=8.3.0",
#     "opencv-python-headless>=4.8.0",
#     "pillow>=10.0.0",
# ]
# ///
"""HaS Image — Privacy anonymization for images via YOLO11 instance segmentation.

Usage:
    uv run has_image.py scan --image photo.jpg [--types face,id_card] [--conf 0.5]
    uv run has_image.py hide --image photo.jpg [--output masked.jpg] [--method mosaic]
    uv run has_image.py hide --dir ./photos/  [--output-dir ./masked/]

See `uv run has_image.py <command> --help` for details.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Category definitions (21 classes)
# ---------------------------------------------------------------------------

CATEGORIES: list[dict[str, str]] = [
    {"id": "0",  "name": "biometric_face",        "zh": "人脸"},
    {"id": "1",  "name": "biometric_fingerprint",  "zh": "指纹"},
    {"id": "2",  "name": "biometric_palmprint",    "zh": "掌纹"},
    {"id": "3",  "name": "id_card",                "zh": "身份证"},
    {"id": "4",  "name": "hk_macau_permit",        "zh": "港澳通行证"},
    {"id": "5",  "name": "passport",               "zh": "护照"},
    {"id": "6",  "name": "employee_badge",         "zh": "工牌"},
    {"id": "7",  "name": "license_plate",          "zh": "车牌"},
    {"id": "8",  "name": "bank_card",              "zh": "银行卡"},
    {"id": "9",  "name": "physical_key",           "zh": "钥匙"},
    {"id": "10", "name": "receipt",                 "zh": "收据"},
    {"id": "11", "name": "shipping_label",          "zh": "快递单"},
    {"id": "12", "name": "official_seal",           "zh": "公章"},
    {"id": "13", "name": "whiteboard",              "zh": "白板"},
    {"id": "14", "name": "sticky_note",             "zh": "便签"},
    {"id": "15", "name": "mobile_screen",           "zh": "手机屏幕"},
    {"id": "16", "name": "monitor_screen",          "zh": "显示器屏幕"},
    {"id": "17", "name": "medical_wristband",       "zh": "医用腕带"},
    {"id": "18", "name": "qr_code",                 "zh": "二维码"},
    {"id": "19", "name": "barcode",                 "zh": "条形码"},
    {"id": "20", "name": "paper",                   "zh": "纸张"},
]

# Build lookup helpers
_ID_TO_CAT = {int(c["id"]): c for c in CATEGORIES}
_NAME_TO_ID = {c["name"]: int(c["id"]) for c in CATEGORIES}
_ZH_TO_ID = {c["zh"]: int(c["id"]) for c in CATEGORIES}
ALL_NAMES = [c["name"] for c in CATEGORIES]


def _resolve_types(types_str: str | None) -> set[int] | None:
    """Parse --types into a set of class IDs, or None (= all)."""
    if not types_str:
        return None
    ids: set[int] = set()
    for token in types_str.split(","):
        token = token.strip()
        if not token:
            continue
        # Try numeric ID
        if token.isdigit():
            cid = int(token)
            if cid in _ID_TO_CAT:
                ids.add(cid)
            else:
                _die(f"Unknown class ID: {cid}")
        # Try english name
        elif token in _NAME_TO_ID:
            ids.add(_NAME_TO_ID[token])
        # Try chinese name
        elif token in _ZH_TO_ID:
            ids.add(_ZH_TO_ID[token])
        # Try partial match (e.g. "face" -> "biometric_face")
        else:
            matches = [n for n in ALL_NAMES if token in n]
            if len(matches) == 1:
                ids.add(_NAME_TO_ID[matches[0]])
            elif len(matches) > 1:
                _die(f"Ambiguous type '{token}', matches: {matches}")
            else:
                _die(
                    f"Unknown type '{token}'. "
                    f"Valid types: {', '.join(ALL_NAMES)}"
                )
    return ids if ids else None


def _die(msg: str) -> None:
    print(f"Error: {msg}", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Model loading
# ---------------------------------------------------------------------------

_MODEL = None
_DEFAULT_MODEL_PATH = os.path.expanduser(
    "~/.openclaw/tools/has-privacy/models/sensitive_seg_best.pt"
)


def _load_model(model_path: str | None = None):
    """Load YOLO11 segmentation model (lazy singleton)."""
    global _MODEL
    if _MODEL is not None:
        return _MODEL

    from ultralytics import YOLO

    path = model_path or os.environ.get("HAS_IMAGE_MODEL", _DEFAULT_MODEL_PATH)
    if not os.path.isfile(path):
        _die(
            f"Model file not found: {path}\n"
            f"Download it via: openclaw install has-privacy "
            f"(or manually from HuggingFace)"
        )
    _MODEL = YOLO(path)
    return _MODEL


# ---------------------------------------------------------------------------
# Detection
# ---------------------------------------------------------------------------

def _run_detection(
    image_path: str,
    model_path: str | None,
    conf: float,
    type_ids: set[int] | None,
) -> dict[str, Any]:
    """Run YOLO detection on a single image and return structured results."""
    import cv2
    import numpy as np

    model = _load_model(model_path)
    results = model(image_path, conf=conf, verbose=False)

    if not results:
        return {"detections": [], "summary": {}}

    result = results[0]
    detections = []
    summary: dict[str, int] = {}

    if result.boxes is not None:
        for i, box in enumerate(result.boxes):
            cls_id = int(box.cls[0].item())
            # Filter by types if specified
            if type_ids is not None and cls_id not in type_ids:
                continue

            cat = _ID_TO_CAT.get(cls_id, {"name": f"unknown_{cls_id}", "zh": "未知"})
            confidence = float(box.conf[0].item())
            bbox = [int(x) for x in box.xyxy[0].tolist()]

            has_mask = (
                result.masks is not None
                and i < len(result.masks.data)
            )

            det = {
                "category": cat["name"],
                "category_zh": cat["zh"],
                "confidence": round(confidence, 4),
                "bbox": bbox,
                "has_mask": has_mask,
            }
            detections.append(det)

            summary[cat["name"]] = summary.get(cat["name"], 0) + 1

    return {"detections": detections, "summary": summary}


# ---------------------------------------------------------------------------
# Masking strategies
# ---------------------------------------------------------------------------

def _apply_mosaic(image, mask, strength: int):
    """Apply mosaic (pixelation) to masked region."""
    import cv2
    import numpy as np

    h, w = image.shape[:2]
    block = max(strength, 2)

    # Downscale then upscale to create pixelation
    small = cv2.resize(image, (max(w // block, 1), max(h // block, 1)),
                       interpolation=cv2.INTER_LINEAR)
    mosaic = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)

    # Apply only within mask
    mask_bool = mask.astype(bool)
    image[mask_bool] = mosaic[mask_bool]
    return image


def _apply_blur(image, mask, strength: int):
    """Apply Gaussian blur to masked region."""
    import cv2
    import numpy as np

    # Kernel size must be odd
    ksize = strength * 2 + 1 if strength % 2 == 0 else strength * 2 - 1
    ksize = max(ksize, 3)

    blurred = cv2.GaussianBlur(image, (ksize, ksize), 0)
    mask_bool = mask.astype(bool)
    image[mask_bool] = blurred[mask_bool]
    return image


def _apply_fill(image, mask, color: tuple[int, int, int]):
    """Apply solid color fill to masked region."""
    mask_bool = mask.astype(bool)
    image[mask_bool] = color
    return image


def _parse_color(color_str: str) -> tuple[int, int, int]:
    """Parse hex color string to BGR tuple (OpenCV format)."""
    color_str = color_str.lstrip("#")
    if len(color_str) != 6:
        _die(f"Invalid color format: #{color_str}. Expected #RRGGBB")
    r = int(color_str[0:2], 16)
    g = int(color_str[2:4], 16)
    b = int(color_str[4:6], 16)
    return (b, g, r)  # BGR for OpenCV


# ---------------------------------------------------------------------------
# Hide (mask) a single image
# ---------------------------------------------------------------------------

def _run_hide(
    image_path: str,
    output_path: str | None,
    model_path: str | None,
    conf: float,
    type_ids: set[int] | None,
    method: str,
    strength: int,
    fill_color: str,
) -> dict[str, Any]:
    """Detect and mask privacy regions in a single image."""
    import cv2
    import numpy as np

    model = _load_model(model_path)
    results = model(image_path, conf=conf, verbose=False)

    image = cv2.imread(image_path)
    if image is None:
        _die(f"Failed to read image: {image_path}")

    h, w = image.shape[:2]
    detections = []
    summary: dict[str, int] = {}

    if results and results[0].boxes is not None:
        result = results[0]

        for i, box in enumerate(result.boxes):
            cls_id = int(box.cls[0].item())
            if type_ids is not None and cls_id not in type_ids:
                continue

            cat = _ID_TO_CAT.get(cls_id, {"name": f"unknown_{cls_id}", "zh": "未知"})
            confidence = float(box.conf[0].item())
            bbox = [int(x) for x in box.xyxy[0].tolist()]

            # Get mask for this detection
            has_mask = result.masks is not None and i < len(result.masks.data)
            if has_mask:
                # Segmentation mask (pixel-level)
                seg_mask = result.masks.data[i].cpu().numpy()
                # Resize mask to image dimensions
                mask = cv2.resize(
                    seg_mask, (w, h), interpolation=cv2.INTER_NEAREST
                ).astype(np.uint8)
            else:
                # Fallback to bounding box mask
                mask = np.zeros((h, w), dtype=np.uint8)
                x1, y1, x2, y2 = bbox
                mask[y1:y2, x1:x2] = 1

            # Apply masking strategy
            if method == "mosaic":
                image = _apply_mosaic(image, mask, strength)
            elif method == "blur":
                image = _apply_blur(image, mask, strength)
            elif method == "fill":
                color = _parse_color(fill_color)
                image = _apply_fill(image, mask, color)

            det = {
                "category": cat["name"],
                "category_zh": cat["zh"],
                "confidence": round(confidence, 4),
                "bbox": bbox,
                "has_mask": has_mask,
            }
            detections.append(det)
            summary[cat["name"]] = summary.get(cat["name"], 0) + 1

    # Determine output path
    if not output_path:
        p = Path(image_path)
        output_path = str(p.parent / "masked" / f"{p.stem}{p.suffix}")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(output_path, image)

    return {
        "output": str(Path(output_path).resolve()),
        "detections": detections,
        "summary": summary,
        "method": method,
        "strength": strength,
    }


# ---------------------------------------------------------------------------
# Batch processing
# ---------------------------------------------------------------------------

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff", ".tif"}


def _iter_images(dir_path: str):
    """Yield image file paths from a directory."""
    d = Path(dir_path)
    if not d.is_dir():
        _die(f"Not a directory: {dir_path}")
    for f in sorted(d.iterdir()):
        if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS:
            yield str(f)


# ---------------------------------------------------------------------------
# Subcommand: detect
# ---------------------------------------------------------------------------

def cmd_scan(args: argparse.Namespace) -> None:
    type_ids = _resolve_types(args.types)
    t0 = time.time()
    result = _run_detection(args.image, args.model, args.conf, type_ids)
    result["elapsed_ms"] = round((time.time() - t0) * 1000)
    _output(result, args.pretty)


# ---------------------------------------------------------------------------
# Subcommand: hide
# ---------------------------------------------------------------------------

def cmd_hide(args: argparse.Namespace) -> None:
    type_ids = _resolve_types(args.types)

    t0 = time.time()
    if args.dir:
        # Batch mode
        output_dir = args.output_dir or str(Path(args.dir) / "masked")
        all_results = []
        for img_path in _iter_images(args.dir):
            fname = Path(img_path).name
            out_path = str(Path(output_dir) / fname)
            result = _run_hide(
                img_path, out_path, args.model,
                args.conf, type_ids, args.method,
                args.strength, args.fill_color,
            )
            all_results.append(result)
        batch_result = {"results": all_results, "count": len(all_results)}
        batch_result["elapsed_ms"] = round((time.time() - t0) * 1000)
        _output(batch_result, args.pretty)
    else:
        # Single image mode
        result = _run_hide(
            args.image, args.output, args.model,
            args.conf, type_ids, args.method,
            args.strength, args.fill_color,
        )
        result["elapsed_ms"] = round((time.time() - t0) * 1000)
        _output(result, args.pretty)


# ---------------------------------------------------------------------------
# Subcommand: categories
# ---------------------------------------------------------------------------

def cmd_categories(args: argparse.Namespace) -> None:
    _output({"categories": CATEGORIES}, args.pretty)


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def _output(data: Any, pretty: bool = False) -> None:
    if pretty:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(data, ensure_ascii=False, separators=(",", ":")))


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="has_image",
        description="HaS Image — Privacy anonymization for images (YOLO11)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  has_image scan --image photo.jpg --types face,id_card\n"
            "  has_image hide --image photo.jpg --method mosaic --strength 20\n"
            "  has_image hide --dir ./photos/ --output-dir ./masked/ --types face\n"
            "  has_image categories\n"
        ),
    )

    parser.add_argument(
        "--pretty", action="store_true", help="Pretty-print JSON output"
    )
    parser.add_argument(
        "--model", default=None,
        help=f"Model file path (env: HAS_IMAGE_MODEL, default: {_DEFAULT_MODEL_PATH})",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- scan ---
    scan_parser = subparsers.add_parser(
        "scan",
        help="Scan image for privacy regions (no masking)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    scan_parser.add_argument("--image", required=True, help="Input image path")
    scan_parser.add_argument(
        "--types", default=None,
        help="Comma-separated category filter (e.g. face,id_card,license_plate). Default: all",
    )
    scan_parser.add_argument(
        "--conf", type=float, default=0.25,
        help="Confidence threshold (default: 0.25)",
    )
    scan_parser.set_defaults(func=cmd_scan)

    # --- hide ---
    hide_parser = subparsers.add_parser(
        "hide",
        help="Detect and mask privacy regions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    img_group = hide_parser.add_mutually_exclusive_group(required=True)
    img_group.add_argument("--image", help="Input image path")
    img_group.add_argument("--dir", help="Input directory for batch processing")
    hide_parser.add_argument("--output", default=None, help="Output image path")
    hide_parser.add_argument("--output-dir", default=None, help="Output directory (batch mode)")
    hide_parser.add_argument(
        "--types", default=None,
        help="Comma-separated category filter (e.g. face,id_card). Default: all",
    )
    hide_parser.add_argument(
        "--method", choices=["mosaic", "blur", "fill"], default="mosaic",
        help="Masking method (default: mosaic)",
    )
    hide_parser.add_argument(
        "--strength", type=int, default=15,
        help="Mosaic block size or blur radius (default: 15)",
    )
    hide_parser.add_argument(
        "--fill-color", default="#000000",
        help="Fill color for 'fill' method, hex format (default: #000000)",
    )
    hide_parser.add_argument(
        "--conf", type=float, default=0.25,
        help="Confidence threshold (default: 0.25)",
    )
    hide_parser.set_defaults(func=cmd_hide)

    # --- categories ---
    cat_parser = subparsers.add_parser(
        "categories",
        help="List all supported privacy categories",
    )
    cat_parser.set_defaults(func=cmd_categories)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
