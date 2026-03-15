#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path

from pypdf import PdfReader


DEFAULT_FILENAMES = {
    "A_滴天髓": "滴天髓.pdf",
    "B_渊海子平": "渊海子平.pdf",
    "C_穷通宝鉴": "穷通宝鉴.pdf",
}


def extract_text(pdf_path: Path) -> list[str]:
    reader = PdfReader(str(pdf_path))
    pages: list[str] = []
    for page in reader.pages:
        pages.append((page.extract_text() or "").strip())
    return pages


def write_txt(pages: list[str], output_txt: Path) -> None:
    lines: list[str] = []
    for index, text in enumerate(pages, start=1):
        lines.append(f"=== PAGE {index} ===")
        lines.append(text)
        lines.append("")
    output_txt.write_text("\n".join(lines), encoding="utf-8")


def write_md(title: str, pages: list[str], output_md: Path) -> None:
    lines: list[str] = [f"# {title}", ""]
    for index, text in enumerate(pages, start=1):
        lines.append(f"## Page {index}")
        lines.append("")
        lines.append(text)
        lines.append("")
    output_md.write_text("\n".join(lines), encoding="utf-8")


def resolve_sources(source_dir: Path) -> dict[str, Path]:
    return {key: source_dir / filename for key, filename in DEFAULT_FILENAMES.items()}


def run(source_dir: Path, output_dir: Path, generate_md: bool) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for key, pdf_path in resolve_sources(source_dir).items():
        if not pdf_path.exists():
            raise FileNotFoundError(f"Missing source pdf: {pdf_path}")
        pages = extract_text(pdf_path)
        txt_path = output_dir / f"{key}.txt"
        write_txt(pages, txt_path)
        if generate_md:
            md_path = output_dir / f"{key}.md"
            write_md(key, pages, md_path)
        print(f"Generated {txt_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract local classic PDFs to UTF-8 txt/md files for fast retrieval."
    )
    parser.add_argument(
        "--source-dir",
        required=True,
        help="Directory containing 滴天髓.pdf / 渊海子平.pdf / 穷通宝鉴.pdf.",
    )
    parser.add_argument(
        "--output-dir",
        default="bazi-daily/references/classics",
        help="Output directory for extracted files.",
    )
    parser.add_argument(
        "--md",
        action="store_true",
        help="Also generate markdown files.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run(Path(args.source_dir), Path(args.output_dir), generate_md=args.md)


if __name__ == "__main__":
    main()
