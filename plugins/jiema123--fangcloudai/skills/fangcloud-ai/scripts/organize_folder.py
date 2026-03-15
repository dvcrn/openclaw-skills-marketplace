#!/usr/bin/env python3
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request


BASE_URL = "https://open.fangcloud.com/api"

DEFAULT_CATEGORY_MAP = {
    "图片": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".heic"},
    "表格": {".xls", ".xlsx", ".csv"},
    "演示": {".ppt", ".pptx", ".key"},
    "文档": {".md", ".txt", ".doc", ".docx", ".pdf", ".rtf", ".xmds"},
    "代码": {".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".go", ".sh", ".yaml", ".yml", ".json", ".xml", ".sql"},
    "压缩包": {".zip", ".rar", ".7z", ".tar", ".gz"},
}


def get_token():
    token = os.environ.get("FANGCLOUD_USER_TOKEN")
    if not token:
        raise RuntimeError("FANGCLOUD_USER_TOKEN not found in environment")
    return token


def api_call(method, path, token, data=None):
    url = f"{BASE_URL}{path}"
    body = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(
        url,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        data=body,
    )
    try:
        with urllib.request.urlopen(req) as resp:
            text = resp.read().decode("utf-8")
            return json.loads(text) if text else {}
    except urllib.error.HTTPError as exc:
        error_text = exc.read().decode("utf-8")
        try:
            payload = json.loads(error_text)
        except Exception:
            payload = {"raw": error_text}
        raise RuntimeError(
            json.dumps(
                {
                    "status": exc.code,
                    "reason": exc.reason,
                    "path": path,
                    "method": method,
                    "data": data,
                    "error": payload,
                },
                ensure_ascii=False,
            )
        )


def extract_folder_id(folder_id, folder_url):
    if folder_id is not None:
        return int(folder_id)
    if not folder_url:
        raise ValueError("Either --folder-id or --folder-url is required")

    decoded = urllib.parse.unquote(folder_url)
    patterns = [
        r"/folder/(\d+)",
        r"preview=(\d+)",
        r"folder_id=(\d+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, decoded)
        if match:
            return int(match.group(1))
    raise ValueError(f"Cannot extract folder id from URL: {folder_url}")


def classify_filename(filename, unknown_category):
    lower_name = (filename or "").lower()
    ext = f".{lower_name.split('.')[-1]}" if "." in lower_name else ""
    for category, extensions in DEFAULT_CATEGORY_MAP.items():
        if ext in extensions:
            return category
    return unknown_category


def list_children(folder_id, token, page_capacity):
    last_error = None
    for start_page in (0, 1):
        try:
            all_files = []
            all_folders = []
            page_id = start_page
            page_count = None

            while True:
                path = (
                    f"/v2/folder/{folder_id}/children"
                    f"?folder_id={folder_id}&type=all&page_capacity={page_capacity}&page_id={page_id}"
                )
                data = api_call("GET", path, token)
                files = data.get("files", [])
                folders = data.get("folders", [])
                all_files.extend(files)
                all_folders.extend(folders)

                if page_count is None:
                    page_count = data.get("page_count")

                if not files and not folders:
                    break

                if isinstance(page_count, int) and page_count > 0:
                    if page_id >= (page_count - 1):
                        break
                else:
                    if len(files) + len(folders) < page_capacity:
                        break

                page_id += 1

            return all_files, all_folders
        except Exception as exc:
            last_error = exc

    raise RuntimeError(f"Failed to list folder children: {last_error}")


def ensure_categories(folder_id, existing_folders, categories, token, dry_run):
    name_to_id = {f.get("name"): f.get("id") for f in existing_folders if f.get("name") and f.get("id")}
    created = []

    for category in sorted(categories):
        if category in name_to_id:
            continue
        if dry_run:
            created.append({"name": category, "id": None, "dry_run": True})
            continue

        resp = api_call(
            "POST",
            "/v2/folder/create",
            token,
            {"name": category, "parent_id": folder_id},
        )
        new_id = resp.get("id")
        if not new_id:
            refreshed_files, refreshed_folders = list_children(folder_id, token, page_capacity=200)
            del refreshed_files
            refreshed = {f.get("name"): f.get("id") for f in refreshed_folders if f.get("name") and f.get("id")}
            if category not in refreshed:
                raise RuntimeError(f"Failed to create category folder: {category}")
            new_id = refreshed[category]

        name_to_id[category] = new_id
        created.append({"name": category, "id": new_id})

    return name_to_id, created


def organize(folder_id, mode, page_capacity, dry_run, unknown_category):
    token = get_token()
    files, folders = list_children(folder_id, token, page_capacity)

    if not files:
        return {
            "root_folder_id": folder_id,
            "mode": mode,
            "initial_file_count": 0,
            "created_folders": [],
            "processed_count": 0,
            "processed_by_category": {},
            "failed_count": 0,
            "failed_samples": [],
            "remaining_files_in_root": 0,
            "dry_run": dry_run,
        }

    file_plan = []
    categories = set()
    for item in files:
        category = classify_filename(item.get("name", ""), unknown_category)
        categories.add(category)
        file_plan.append(
            {
                "id": item.get("id"),
                "name": item.get("name", ""),
                "category": category,
            }
        )

    name_to_id, created = ensure_categories(folder_id, folders, categories, token, dry_run)

    processed = 0
    failed = []
    processed_by_category = {}

    for item in file_plan:
        file_id = item["id"]
        category = item["category"]
        target_folder_id = name_to_id.get(category)
        if not file_id or not target_folder_id:
            failed.append({"id": file_id, "name": item["name"], "reason": "missing_target"})
            continue

        if dry_run:
            processed += 1
            processed_by_category[category] = processed_by_category.get(category, 0) + 1
            continue

        endpoint = f"/v2/file/{file_id}/{mode}"
        try:
            api_call("POST", endpoint, token, {"target_folder_id": target_folder_id})
            processed += 1
            processed_by_category[category] = processed_by_category.get(category, 0) + 1
        except Exception as exc:
            failed.append({"id": file_id, "name": item["name"], "category": category, "error": str(exc)})

    verify_files, verify_folders = list_children(folder_id, token, page_capacity)
    del verify_folders

    return {
        "root_folder_id": folder_id,
        "mode": mode,
        "initial_file_count": len(files),
        "categories": sorted(categories),
        "created_folders": created,
        "processed_count": processed,
        "processed_by_category": processed_by_category,
        "failed_count": len(failed),
        "failed_samples": failed[:10],
        "remaining_files_in_root": len(verify_files),
        "dry_run": dry_run,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Auto-organize Fangcloud folder by file extension categories"
    )
    parser.add_argument("--folder-id", type=int, help="Target folder ID")
    parser.add_argument("--folder-url", help="Target folder URL containing folder id")
    parser.add_argument("--mode", choices=["move", "copy"], default="move", help="Use move or copy (default: move)")
    parser.add_argument("--page-capacity", type=int, default=200, help="Page size for listing children (default: 200)")
    parser.add_argument("--unknown-category", default="其他", help="Category folder name for unknown extensions")
    parser.add_argument("--dry-run", action="store_true", help="Preview plan without creating/moving/copying files")

    args = parser.parse_args()

    try:
        folder_id = extract_folder_id(args.folder_id, args.folder_url)
        result = organize(
            folder_id=folder_id,
            mode=args.mode,
            page_capacity=args.page_capacity,
            dry_run=args.dry_run,
            unknown_category=args.unknown_category,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
