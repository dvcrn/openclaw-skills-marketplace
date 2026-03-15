#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PLUGIN_ROOT_ENTRIES = {
    ".lsp.json",
    ".mcp.json",
    "agents",
    "commands",
    "hooks",
    "settings.json",
}

EXCLUDED_NAMES = {
    ".DS_Store",
    ".claude",
    ".claude-plugin",
    ".git",
    ".github",
    "__pycache__",
    "_meta.json",
}


@dataclass(frozen=True)
class SourceSkill:
    owner: str
    slug: str
    display_name: str
    version: str
    source_dir: Path
    skill_filename: str
    frontmatter: dict[str, str]
    body: str
    raw_text: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a Claude plugin marketplace from the OpenClaw skills tree."
    )
    parser.add_argument(
        "--source",
        default="openclaw-skills/skills",
        help="Path to the OpenClaw skills source tree.",
    )
    parser.add_argument(
        "--output",
        default=".",
        help="Path to the marketplace output repository root.",
    )
    parser.add_argument(
        "--marketplace-name",
        default="openclaw-skills",
        help="Marketplace identifier written to .claude-plugin/marketplace.json.",
    )
    parser.add_argument(
        "--owner-name",
        default="OpenClaw",
        help="Marketplace owner name written to .claude-plugin/marketplace.json.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional limit for development runs.",
    )
    return parser.parse_args()


def sanitize_segment(value: str, default: str) -> str:
    sanitized = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return sanitized or default


def list_exact_children(directory: Path) -> list[str]:
    return sorted(entry.name for entry in directory.iterdir())


def detect_skill_filename(directory: Path) -> str | None:
    children = set(list_exact_children(directory))
    if "SKILL.md" in children:
        return "SKILL.md"
    if "skill.md" in children:
        return "skill.md"
    return None


def strip_quotes(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def parse_yaml_like_frontmatter(raw_frontmatter: str) -> dict[str, str]:
    result: dict[str, str] = {}
    lines = raw_frontmatter.splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        if not line.strip() or line.lstrip().startswith("#"):
            index += 1
            continue
        if line.startswith((" ", "\t")) or ":" not in line:
            index += 1
            continue

        key, rest = line.split(":", 1)
        key = key.strip()
        rest = rest.strip()
        if not key:
            index += 1
            continue

        if rest in {"|", "|-", "|+", ">", ">-", ">+"}:
            block_lines: list[str] = []
            index += 1
            while index < len(lines):
                candidate = lines[index]
                if candidate.startswith((" ", "\t")) or not candidate.strip():
                    block_lines.append(candidate[1:] if candidate.startswith(" ") else candidate)
                    index += 1
                    continue
                break
            if rest.startswith(">"):
                result[key] = " ".join(part.strip() for part in block_lines if part.strip())
            else:
                result[key] = "\n".join(block_lines).rstrip("\n")
            continue

        result[key] = strip_quotes(rest)
        index += 1
    return result


def split_frontmatter(text: str) -> tuple[str | None, str]:
    if not text.startswith("---\n") and text != "---":
        return None, text

    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return None, text

    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            frontmatter = "".join(lines[1:index])
            body = "".join(lines[index + 1 :])
            return frontmatter, body
    return None, text


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(load_text(path))


def synthesize_skill_markdown(
    body: str,
    existing_frontmatter: dict[str, str],
    fallback_name: str,
    fallback_description: str | None,
) -> str:
    name = existing_frontmatter.get("name", fallback_name).strip() or fallback_name
    description = (
        existing_frontmatter.get("description", "").strip()
        or (fallback_description or "").strip()
    )
    if not description:
        raise ValueError("missing skill description")

    header_lines = ["---", f"name: {name}", f"description: {json.dumps(description, ensure_ascii=False)}"]
    homepage = existing_frontmatter.get("homepage", "").strip()
    if homepage:
        header_lines.append(f"homepage: {homepage}")
    header_lines.append("---")
    return "\n".join(header_lines) + "\n\n" + body.lstrip("\n")


def rewrite_primary_skill_paths(body: str, root_entries: set[str]) -> str:
    rewritten = body
    prefix = "../../"
    for name in sorted(root_entries, key=len, reverse=True):
        escaped = re.escape(name)
        rewritten = re.sub(
            rf"`({escaped}(?:/[^`\n]+)?)`",
            lambda match: f"`{prefix}{match.group(1)}`",
            rewritten,
        )
        rewritten = re.sub(
            rf"\((?!https?://|#|/)\s*({escaped}(?:/[^)\s]+)?)\s*\)",
            lambda match: f"({prefix}{match.group(1)})",
            rewritten,
        )
    return rewritten


def remove_path(path: Path) -> None:
    if not path.exists() and not path.is_symlink():
        return
    if path.is_symlink() or path.is_file():
        path.unlink()
        return
    shutil.rmtree(path)


def copy_tree(
    src: Path,
    dst: Path,
    report: dict[str, Any],
    normalize_skill_files: bool = True,
) -> None:
    if src.name in EXCLUDED_NAMES:
        return

    if src.is_dir():
        dst.mkdir(parents=True, exist_ok=True)
        for child in sorted(src.iterdir(), key=lambda item: item.name):
            if child.name in EXCLUDED_NAMES:
                continue
            child_dst_name = "SKILL.md" if normalize_skill_files and child.name == "skill.md" else child.name
            copy_tree(child, dst / child_dst_name, report, normalize_skill_files=normalize_skill_files)
        return

    dst.parent.mkdir(parents=True, exist_ok=True)
    if normalize_skill_files and src.name == "skill.md":
        report["normalized_skill_files"] += 1
    shutil.copy2(src, dst)


def make_plugin_id(owner: str, slug: str, used_ids: set[str], report: dict[str, Any]) -> str:
    base = f"{sanitize_segment(owner, 'owner')}--{sanitize_segment(slug, 'skill')}"
    if base not in used_ids:
        used_ids.add(base)
        return base

    suffix = hashlib.sha1(f"{owner}/{slug}".encode("utf-8")).hexdigest()[:8]
    candidate = f"{base}-{suffix}"
    if candidate in used_ids:
        raise ValueError(f"unrecoverable plugin id collision for {owner}/{slug}")

    used_ids.add(candidate)
    report["collision_resolutions"].append(
        {"owner": owner, "slug": slug, "plugin_id": candidate, "base_plugin_id": base}
    )
    return candidate


def load_source_skill(source_dir: Path) -> SourceSkill:
    metadata = load_json(source_dir / "_meta.json")
    owner = metadata["owner"]
    slug = metadata["slug"]
    display_name = metadata.get("displayName", slug)
    version = metadata["latest"]["version"]

    skill_filename = detect_skill_filename(source_dir)
    if not skill_filename:
        raise ValueError("missing root SKILL.md/skill.md")

    raw_text = load_text(source_dir / skill_filename)
    raw_frontmatter, body = split_frontmatter(raw_text)
    frontmatter = parse_yaml_like_frontmatter(raw_frontmatter or "")

    return SourceSkill(
        owner=owner,
        slug=slug,
        display_name=display_name,
        version=version,
        source_dir=source_dir,
        skill_filename=skill_filename,
        frontmatter=frontmatter,
        body=body,
        raw_text=raw_text,
    )


def primary_skill_dir_name(source: SourceSkill, existing_nested_names: set[str]) -> str:
    preferred = sanitize_segment(source.frontmatter.get("name", source.slug), "skill")
    if preferred not in existing_nested_names:
        return preferred

    fallback = f"{sanitize_segment(source.slug, 'skill')}-root"
    if fallback not in existing_nested_names:
        return fallback

    suffix = hashlib.sha1(
        f"{source.owner}/{source.slug}/{preferred}".encode("utf-8")
    ).hexdigest()[:8]
    return f"{fallback}-{suffix}"


def build_plugin(
    source: SourceSkill,
    plugins_dir: Path,
    used_ids: set[str],
    report: dict[str, Any],
) -> dict[str, str]:
    plugin_id = make_plugin_id(source.owner, source.slug, used_ids, report)
    plugin_dir = plugins_dir / plugin_id
    (plugin_dir / ".claude-plugin").mkdir(parents=True, exist_ok=True)

    nested_skills_dir = source.source_dir / "skills"
    has_nested_skills = nested_skills_dir.is_dir()
    nested_skill_names = (
        {sanitize_segment(child.name, "skill") for child in nested_skills_dir.iterdir() if child.is_dir()}
        if has_nested_skills
        else set()
    )
    primary_dir_name = primary_skill_dir_name(source, nested_skill_names)
    primary_skill_dir = plugin_dir / "skills" / primary_dir_name
    primary_skill_dir.mkdir(parents=True, exist_ok=True)

    root_entries_to_copy: set[str] = set()
    for entry_name in list_exact_children(source.source_dir):
        if entry_name in EXCLUDED_NAMES or entry_name == source.skill_filename:
            continue
        root_entries_to_copy.add(entry_name)

        src_entry = source.source_dir / entry_name
        if has_nested_skills:
            dst_entry = plugin_dir / entry_name
            copy_tree(src_entry, dst_entry, report)
            continue

        dst_entry = (
            plugin_dir / entry_name
            if entry_name in PLUGIN_ROOT_ENTRIES
            else primary_skill_dir / ("SKILL.md" if entry_name == "skill.md" else entry_name)
        )
        copy_tree(src_entry, dst_entry, report)

    primary_body = source.body
    if has_nested_skills:
        primary_body = rewrite_primary_skill_paths(primary_body, root_entries_to_copy)
        note = (
            "> Generated note: shared plugin assets for this package live at the plugin root. "
            "Common local references were rewritten when they appeared in backticks or markdown links.\n\n"
        )
        primary_body = note + primary_body.lstrip("\n")

    primary_skill_text = synthesize_skill_markdown(
        body=primary_body,
        existing_frontmatter=source.frontmatter,
        fallback_name=source.frontmatter.get("name", source.slug),
        fallback_description=source.frontmatter.get("description") or source.display_name,
    )
    (primary_skill_dir / "SKILL.md").write_text(primary_skill_text, encoding="utf-8")
    if source.skill_filename == "skill.md":
        report["normalized_skill_files"] += 1

    description = source.frontmatter.get("description", "").strip() or source.display_name
    homepage = source.frontmatter.get(
        "homepage",
        f"https://github.com/openclaw/skills/tree/main/skills/{source.owner}/{source.slug}",
    )
    source_url = f"https://github.com/openclaw/skills/tree/main/skills/{source.owner}/{source.slug}"
    plugin_manifest = {
        "name": plugin_id,
        "description": description,
        "version": source.version,
        "author": {"name": source.owner},
        "homepage": homepage,
        "repository": source_url,
    }
    (plugin_dir / ".claude-plugin" / "plugin.json").write_text(
        json.dumps(plugin_manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    report["generated_plugins"].append(
        {
            "owner": source.owner,
            "slug": source.slug,
            "plugin_id": plugin_id,
            "primary_skill_dir": primary_dir_name,
        }
    )
    return {"name": plugin_id, "description": description, "source": f"./plugins/{plugin_id}"}


def discover_source_dirs(source_root: Path) -> list[Path]:
    source_dirs: list[Path] = []
    for owner_dir in sorted(source_root.iterdir(), key=lambda item: item.name):
        if not owner_dir.is_dir():
            continue
        for skill_dir in sorted(owner_dir.iterdir(), key=lambda item: item.name):
            if skill_dir.is_dir() and (skill_dir / "_meta.json").is_file():
                source_dirs.append(skill_dir)
    return source_dirs


def generate_marketplace(
    source_root: Path,
    output_root: Path,
    marketplace_name: str,
    owner_name: str,
    limit: int | None = None,
) -> dict[str, Any]:
    source_root = source_root.resolve()
    output_root = output_root.resolve()

    discovered = discover_source_dirs(source_root)
    if limit is not None:
        discovered = discovered[:limit]

    report: dict[str, Any] = {
        "marketplace_name": marketplace_name,
        "source_root": str(source_root),
        "output_root": str(output_root),
        "total_source_skills": len(discovered),
        "generated_count": 0,
        "skipped_count": 0,
        "normalized_skill_files": 0,
        "collision_resolutions": [],
        "generated_plugins": [],
        "skipped": [],
    }

    with tempfile.TemporaryDirectory(prefix="generate-marketplace-") as temp_dir:
        build_root = Path(temp_dir)
        plugins_dir = build_root / "plugins"
        marketplace_dir = build_root / ".claude-plugin"
        reports_dir = build_root / "reports"
        plugins_dir.mkdir(parents=True, exist_ok=True)
        marketplace_dir.mkdir(parents=True, exist_ok=True)
        reports_dir.mkdir(parents=True, exist_ok=True)

        used_ids: set[str] = set()
        plugin_entries: list[dict[str, str]] = []

        for source_dir in discovered:
            rel_dir = source_dir.relative_to(source_root)
            try:
                source = load_source_skill(source_dir)
                plugin_entries.append(build_plugin(source, plugins_dir, used_ids, report))
            except Exception as exc:  # noqa: BLE001
                report["skipped"].append({"source": str(rel_dir), "reason": str(exc)})

        report["generated_count"] = len(plugin_entries)
        report["skipped_count"] = len(report["skipped"])

        if report["generated_count"] == 0:
            raise RuntimeError("generator did not produce any plugins")

        marketplace_manifest = {
            "name": marketplace_name,
            "owner": {"name": owner_name},
            "metadata": {
                "description": f"Generated Claude plugin marketplace from {marketplace_name}",
            },
            "plugins": plugin_entries,
        }
        (marketplace_dir / "marketplace.json").write_text(
            json.dumps(marketplace_manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (reports_dir / "generate-marketplace.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        output_root.mkdir(parents=True, exist_ok=True)
        for managed in [".claude-plugin", "plugins", "reports"]:
            remove_path(output_root / managed)
            shutil.move(str(build_root / managed), str(output_root / managed))

    return report


def main() -> int:
    args = parse_args()
    report = generate_marketplace(
        source_root=Path(args.source),
        output_root=Path(args.output),
        marketplace_name=args.marketplace_name,
        owner_name=args.owner_name,
        limit=args.limit,
    )
    print(
        json.dumps(
            {
                "generated_count": report["generated_count"],
                "skipped_count": report["skipped_count"],
                "normalized_skill_files": report["normalized_skill_files"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
