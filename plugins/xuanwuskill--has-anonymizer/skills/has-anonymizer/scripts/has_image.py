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


def _is_within_directory(path: Path, directory: Path) -> bool:
    """Return whether `path` resolves within `directory`."""
    try:
        path.relative_to(directory)
        return True
    except ValueError:
        return False


# ---------------------------------------------------------------------------
# Model loading
# ---------------------------------------------------------------------------

_MODEL = None
_MODEL_LOCK = __import__("threading").Lock()
_DEFAULT_MODEL_PATH = os.path.expanduser(
    "~/.openclaw/tools/has-anonymizer/models/sensitive_seg_best.pt"
)


def _load_model(model_path: str | None = None):
    """Load YOLO11 segmentation model (lazy singleton, thread-safe)."""
    global _MODEL
    if _MODEL is not None:
        return _MODEL

    with _MODEL_LOCK:
        # Double-check after acquiring the lock.
        if _MODEL is not None:
            return _MODEL

        from ultralytics import YOLO

        path = model_path or os.environ.get("HAS_IMAGE_MODEL", _DEFAULT_MODEL_PATH)
        if not os.path.isfile(path):
            _die(
                f"Model file not found: {path}\n"
                f"Download it via: openclaw install has-anonymizer "
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
    model = _load_model(model_path)
    results = model(image_path, conf=conf, verbose=False)

    if not results:
        return {"detections": [], "summary": {}}

    result = results[0]
    detections = []
    summary: dict[str, int] = {}

    for _, _, det in _iter_detection_regions(result, type_ids):
        detections.append(det)
        summary[det["category"]] = summary.get(det["category"], 0) + 1

    return {"detections": detections, "summary": summary}


def _iter_detection_regions(result, type_ids: set[int] | None):
    """Yield filtered detection metadata shared by scan/hide."""

    if result.boxes is None:
        return

    for index, box in enumerate(result.boxes):
        cls_id = int(box.cls[0].item())
        if type_ids is not None and cls_id not in type_ids:
            continue

        cat = _ID_TO_CAT.get(cls_id, {"name": f"unknown_{cls_id}", "zh": "未知"})
        confidence = float(box.conf[0].item())
        bbox = [int(x) for x in box.xyxy[0].tolist()]
        has_mask = result.masks is not None and index < len(result.masks.data)

        yield index, bbox, {
            "category": cat["name"],
            "category_zh": cat["zh"],
            "confidence": round(confidence, 4),
            "bbox": bbox,
            "has_mask": has_mask,
        }


def _build_detection_mask(result, index: int, bbox: list[int], image_shape: tuple[int, int]):
    """Build a segmentation or bbox mask for a detection."""

    import cv2
    import numpy as np

    h, w = image_shape
    has_mask = result.masks is not None and index < len(result.masks.data)
    if has_mask:
        seg_mask = result.masks.data[index].cpu().numpy()
        return cv2.resize(seg_mask, (w, h), interpolation=cv2.INTER_NEAREST).astype(np.uint8)

    mask = np.zeros((h, w), dtype=np.uint8)
    x1, y1, x2, y2 = bbox
    mask[y1:y2, x1:x2] = 1
    return mask


def _resolve_output_path(image_path: str, output_path: str | None) -> str:
    """Resolve the output path and refuse to overwrite the source image."""

    image = Path(image_path)
    target = Path(output_path) if output_path else image.parent / "masked" / f"{image.stem}{image.suffix}"

    if target.resolve(strict=False) == image.resolve(strict=False):
        _die("Refusing to overwrite the original image; choose a different output path")

    return str(target)


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

    # Kernel size must be odd; ensure a monotonic relationship with strength
    ksize = max(strength | 1, 3)

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
    try:
        r = int(color_str[0:2], 16)
        g = int(color_str[2:4], 16)
        b = int(color_str[4:6], 16)
    except ValueError:
        _die(f"Invalid color format: #{color_str}. Expected #RRGGBB")
    return (b, g, r)  # BGR for OpenCV


def _resolve_fill_color(method: str, fill_color: str) -> tuple[int, int, int] | None:
    """Validate fill settings before any model work starts."""
    if method != "fill":
        return None
    return _parse_color(fill_color)


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
    fill_color: tuple[int, int, int] | None,
) -> dict[str, Any]:
    """Detect and mask privacy regions in a single image."""
    import cv2

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

        for index, bbox, det in _iter_detection_regions(result, type_ids):
            mask = _build_detection_mask(result, index, bbox, (h, w))

            # Apply masking strategy
            if method == "mosaic":
                image = _apply_mosaic(image, mask, strength)
            elif method == "blur":
                image = _apply_blur(image, mask, strength)
            elif method == "fill":
                if fill_color is None:
                    _die("Fill color is required when --method=fill")
                image = _apply_fill(image, mask, fill_color)

            detections.append(det)
            summary[det["category"]] = summary.get(det["category"], 0) + 1

    output_path = _resolve_output_path(image_path, output_path)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(output_path, image):
        _die(f"Failed to write masked image: {output_path}")

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
    root = d.resolve()
    for f in sorted(d.iterdir()):
        if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS:
            try:
                resolved = f.resolve()
            except OSError:
                continue
            if not _is_within_directory(resolved, root):
                continue
            yield str(f)


def run_scan_batch(
    image_paths: list[str],
    model_path: str | None,
    conf: float,
    type_ids: set[int] | None,
) -> dict[str, Any]:
    """Scan a batch of images serially while preserving input order."""
    if not image_paths:
        return {"results": [], "count": 0, "summary": {}}

    results = []
    for image_path in image_paths:
        result = _run_detection(image_path, model_path, conf, type_ids)
        result["file"] = image_path
        results.append(result)

    merged_summary: dict[str, int] = {}
    for result in results:
        for cat, count in result.get("summary", {}).items():
            merged_summary[cat] = merged_summary.get(cat, 0) + count

    return {
        "results": results,
        "count": len(results),
        "summary": merged_summary,
    }


def run_hide_batch(
    image_paths: list[str],
    output_dir: str,
    model_path: str | None,
    conf: float,
    type_ids: set[int] | None,
    method: str,
    strength: int,
    fill_color: tuple[int, int, int] | None,
) -> dict[str, Any]:
    """Hide privacy regions in a batch of images serially while preserving input order."""
    if not image_paths:
        return {"results": [], "count": 0}

    results = []
    for image_path in image_paths:
        output_path = str(Path(output_dir) / Path(image_path).name)
        result = _run_hide(
            image_path,
            output_path,
            model_path,
            conf,
            type_ids,
            method,
            strength,
            fill_color,
        )
        result["file"] = image_path
        results.append(result)

    return {"results": results, "count": len(results)}


# ---------------------------------------------------------------------------
# Subcommand: detect
# ---------------------------------------------------------------------------

def cmd_scan(args: argparse.Namespace) -> None:
    type_ids = _resolve_types(args.types)

    t0 = time.time()
    if args.dir:
        batch_result = run_scan_batch(
            list(_iter_images(args.dir)),
            args.model,
            args.conf,
            type_ids,
        )
        batch_result["elapsed_ms"] = round((time.time() - t0) * 1000)
        _output(batch_result, args.pretty)
    else:
        # Single image mode
        result = _run_detection(args.image, args.model, args.conf, type_ids)
        result["elapsed_ms"] = round((time.time() - t0) * 1000)
        _output(result, args.pretty)


# ---------------------------------------------------------------------------
# Subcommand: hide
# ---------------------------------------------------------------------------

def cmd_hide(args: argparse.Namespace) -> None:
    type_ids = _resolve_types(args.types)
    fill_color = _resolve_fill_color(args.method, args.fill_color)

    t0 = time.time()
    if args.dir:
        output_dir = args.output_dir or str(Path(args.dir) / "masked")
        batch_result = run_hide_batch(
            list(_iter_images(args.dir)),
            output_dir,
            args.model,
            args.conf,
            type_ids,
            args.method,
            args.strength,
            fill_color,
        )
        batch_result["elapsed_ms"] = round((time.time() - t0) * 1000)
        _output(batch_result, args.pretty)
    else:
        # Single image mode
        result = _run_hide(
            args.image, args.output, args.model,
            args.conf, type_ids, args.method,
            args.strength, fill_color,
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
    scan_img_group = scan_parser.add_mutually_exclusive_group(required=True)
    scan_img_group.add_argument("--image", help="Input image path")
    scan_img_group.add_argument("--dir", help="Input directory for batch scanning")
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
