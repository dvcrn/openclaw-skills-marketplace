#!/usr/bin/env python3
import argparse
import difflib
import json
import mimetypes
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request


BASE_URL = "https://open.fangcloud.com/api"


def get_token():
    token = os.environ.get("FANGCLOUD_USER_TOKEN")
    if not token:
        raise RuntimeError("FANGCLOUD_USER_TOKEN not found in environment")
    return token


def resolve_local_dir(local_dir):
    expanded = os.path.expanduser(local_dir)
    if os.path.isdir(expanded):
        return os.path.abspath(expanded), None

    parent = os.path.dirname(expanded)
    target = os.path.basename(expanded)
    if not os.path.isdir(parent):
        raise FileNotFoundError(f"Local directory not found: {expanded}")

    siblings = [name for name in os.listdir(parent) if os.path.isdir(os.path.join(parent, name))]
    guesses = difflib.get_close_matches(target, siblings, n=1, cutoff=0.6)
    if guesses:
        guessed = os.path.abspath(os.path.join(parent, guesses[0]))
        return guessed, expanded

    raise FileNotFoundError(f"Local directory not found: {expanded}")


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
            payload = resp.read().decode("utf-8")
            return json.loads(payload) if payload else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8")
        try:
            parsed = json.loads(detail)
        except Exception:
            parsed = {"raw": detail}
        raise RuntimeError(
            json.dumps(
                {
                    "status": exc.code,
                    "reason": exc.reason,
                    "method": method,
                    "path": path,
                    "data": data,
                    "error": parsed,
                },
                ensure_ascii=False,
            )
        )


def find_upload_url(obj):
    if isinstance(obj, str):
        if obj.startswith("http") and "upload" in obj:
            return obj
        return None
    if isinstance(obj, dict):
        for value in obj.values():
            found = find_upload_url(value)
            if found:
                return found
        return None
    if isinstance(obj, list):
        for value in obj:
            found = find_upload_url(value)
            if found:
                return found
        return None
    return None


def sanitize_name(name):
    illegal = '/?:*"<>|'
    out = "".join("_" if ch in illegal else ch for ch in name)
    out = out.rstrip(".")
    return out[:222] if len(out) > 222 else out


def build_rename(name):
    base, ext = os.path.splitext(name)
    suffix = time.strftime("%Y%m%d%H%M%S")
    return sanitize_name(f"{base}__reupload_{suffix}{ext}")


def create_folder_by_path(token, folder_path):
    return api_call(
        "POST",
        "/v2/folder/create_by_path",
        token,
        {"target_folder_path": folder_path},
    )


def create_folder(token, parent_id, name):
    return api_call(
        "POST",
        "/v2/folder/create",
        token,
        {
            "name": name,
            "parent_id": int(parent_id),
        },
    )


def list_folder_children(token, folder_id):
    page_id = 0
    page_capacity = 100
    items = []

    while True:
        query = urllib.parse.urlencode({"page_id": page_id, "page_capacity": page_capacity})
        resp = api_call("GET", f"/v2/folder/{int(folder_id)}/children?{query}", token)
        page_items = resp.get("files", []) + resp.get("folders", [])
        items.extend(page_items)

        page_count = int(resp.get("page_count", 1) or 1)
        if page_id + 1 >= page_count:
            break
        page_id += 1

    return items


def find_child_folder_id(token, parent_id, name):
    for item in list_folder_children(token, parent_id):
        if item.get("type") != "folder":
            continue
        if item.get("name") != name:
            continue
        if item.get("in_trash"):
            continue
        return int(item["id"])
    return None


def ensure_child_folder(token, parent_id, name):
    existing = find_child_folder_id(token, parent_id, name)
    if existing is not None:
        return existing

    created = create_folder(token, parent_id, name)
    created_id = created.get("id")
    if created_id is None:
        raise RuntimeError(f"create folder response missing id for {name} under parent {parent_id}")
    return int(created_id)


def init_upload_by_path(token, folder_path, name, overwrite):
    payload = {
        "target_folder_path": folder_path,
        "name": name,
        "upload_type": "api",
    }
    if overwrite:
        payload["is_covered"] = True

    return api_call("POST", "/v2/file/upload_by_path", token, payload)


def init_upload_by_parent_id(token, parent_id, name, overwrite):
    payload = {
        "parent_id": int(parent_id),
        "name": name,
        "upload_type": "api",
    }
    if overwrite:
        payload["is_covered"] = True

    return api_call("POST", "/v2/file/upload_v2", token, payload)


def upload_file_to_url(upload_url, file_path):
    mime = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
    cmd = [
        "curl",
        "-sS",
        "-X",
        "POST",
        upload_url,
        "-F",
        f"file=@{file_path};type={mime}",
    ]
    run = subprocess.run(cmd, capture_output=True, text=True)
    if run.returncode == 0:
        return

    fallback_cmd = [
        "curl",
        "-sS",
        "--tlsv1.2",
        "--ciphers",
        "DEFAULT@SECLEVEL=1",
        "-X",
        "POST",
        upload_url,
        "-F",
        f"file=@{file_path};type={mime}",
    ]
    fallback_run = subprocess.run(fallback_cmd, capture_output=True, text=True)
    if fallback_run.returncode != 0:
        err_text = (fallback_run.stderr or fallback_run.stdout or run.stderr or run.stdout).strip()
        raise RuntimeError(err_text if err_text else "curl upload failed")


def collect_files(local_root, include_hidden):
    file_list = []
    for root, dirs, files in os.walk(local_root):
        if not include_hidden:
            dirs[:] = [name for name in dirs if not name.startswith(".")]
            files = [name for name in files if not name.startswith(".")]

        for name in files:
            abs_path = os.path.join(root, name)
            rel_path = os.path.relpath(abs_path, local_root)
            file_list.append((abs_path, rel_path))
    return sorted(file_list, key=lambda x: x[1])


def upload_directory(local_dir, remote_root, remote_parent_id, dry_run, conflict_strategy, include_hidden):
    token = get_token()
    resolved_local, original_missing = resolve_local_dir(local_dir)
    local_name = os.path.basename(resolved_local)
    use_parent_id_mode = remote_parent_id is not None
    remote_base = f"{remote_root}/{local_name}" if remote_root else local_name
    remote_base_folder_id = None

    if use_parent_id_mode and remote_root:
        raise ValueError("--remote-root and --remote-parent-id cannot be used together")

    all_files = collect_files(resolved_local, include_hidden)

    ensured_folders = set()
    ensured_folder_ids = {}
    dry_run_next_folder_id = -1

    if use_parent_id_mode:
        if dry_run:
            remote_base_folder_id = dry_run_next_folder_id
            dry_run_next_folder_id -= 1
        else:
            remote_base_folder_id = ensure_child_folder(token, int(remote_parent_id), local_name)

    uploaded = []
    failed = []

    for abs_path, rel_path in all_files:
        rel_folder = os.path.dirname(rel_path).replace(os.sep, "/")

        target_folder = None
        target_folder_id = None

        if use_parent_id_mode:
            rel_parts = [] if rel_folder in ("", ".") else [part for part in rel_folder.split("/") if part]
            current_id = remote_base_folder_id
            current_path = local_name

            for part in rel_parts:
                key = (current_id, part)
                if key not in ensured_folder_ids:
                    if dry_run:
                        ensured_folder_ids[key] = dry_run_next_folder_id
                        dry_run_next_folder_id -= 1
                    else:
                        ensured_folder_ids[key] = ensure_child_folder(token, current_id, part)

                current_id = ensured_folder_ids[key]
                current_path = f"{current_path}/{part}"

            target_folder_id = current_id
            target_folder = current_path
        else:
            target_folder = remote_base if rel_folder in ("", ".") else f"{remote_base}/{rel_folder}"
            target_folder = target_folder.strip("/")

            if target_folder not in ensured_folders:
                if not dry_run:
                    create_folder_by_path(token, target_folder)
                ensured_folders.add(target_folder)

        name = sanitize_name(os.path.basename(abs_path))
        upload_name = name
        retried = False
        overwrite = conflict_strategy == "overwrite"

        try:
            if not dry_run:
                if use_parent_id_mode:
                    init_resp = init_upload_by_parent_id(token, target_folder_id, upload_name, overwrite)
                else:
                    init_resp = init_upload_by_path(token, target_folder, upload_name, overwrite)
                upload_url = find_upload_url(init_resp)
                if not upload_url:
                    raise RuntimeError(f"Upload URL not found in init response for {rel_path}")
                upload_file_to_url(upload_url, abs_path)

            uploaded.append(
                {
                    "local": rel_path,
                    "remote_folder": target_folder,
                    "remote_folder_id": target_folder_id,
                    "remote_name": upload_name,
                    "renamed_on_conflict": False,
                }
            )
        except Exception as first_error:
            if overwrite:
                failed.append(
                    {
                        "local": rel_path,
                        "remote_folder": target_folder,
                        "remote_folder_id": target_folder_id,
                        "first_error": str(first_error),
                        "second_error": None,
                        "retried_with_rename": False,
                    }
                )
                continue

            upload_name = build_rename(name)
            retried = True
            try:
                if not dry_run:
                    if use_parent_id_mode:
                        init_resp = init_upload_by_parent_id(token, target_folder_id, upload_name, overwrite=False)
                    else:
                        init_resp = init_upload_by_path(token, target_folder, upload_name, overwrite=False)
                    upload_url = find_upload_url(init_resp)
                    if not upload_url:
                        raise RuntimeError(f"Upload URL not found in retry response for {rel_path}")
                    upload_file_to_url(upload_url, abs_path)

                uploaded.append(
                    {
                        "local": rel_path,
                        "remote_folder": target_folder,
                        "remote_folder_id": target_folder_id,
                        "remote_name": upload_name,
                        "renamed_on_conflict": True,
                    }
                )
            except Exception as second_error:
                failed.append(
                    {
                        "local": rel_path,
                        "remote_folder": target_folder,
                        "remote_folder_id": target_folder_id,
                        "first_error": str(first_error),
                        "second_error": str(second_error),
                        "retried_with_rename": retried,
                    }
                )

    return {
        "local_input": local_dir,
        "resolved_local": resolved_local,
        "path_autocorrected": bool(original_missing),
        "original_missing_path": original_missing,
        "remote_mode": "parent_id" if use_parent_id_mode else "path",
        "remote_parent_id": int(remote_parent_id) if remote_parent_id is not None else None,
        "remote_base_folder_id": remote_base_folder_id,
        "remote_base_folder": remote_base,
        "conflict_strategy": conflict_strategy,
        "include_hidden": include_hidden,
        "dry_run": dry_run,
        "total_files": len(all_files),
        "uploaded_count": len(uploaded),
        "failed_count": len(failed),
        "rename_retry_count": sum(1 for x in uploaded if x["renamed_on_conflict"]),
        "failed_samples": failed[:10],
        "uploaded_samples": uploaded[:20],
    }


def main():
    parser = argparse.ArgumentParser(description="Upload a local directory to Fangcloud personal space")
    parser.add_argument("local_dir", help="Local directory path")
    parser.add_argument("--remote-root", default="", help="Remote parent path under personal space")
    parser.add_argument("--remote-parent-id", type=int, default=None, help="Remote parent folder ID under personal space")
    parser.add_argument(
        "--conflict-strategy",
        choices=["overwrite", "rename"],
        default="overwrite",
        help="Same-name upload strategy: overwrite(existing as new version) or rename",
    )
    parser.add_argument(
        "--include-hidden",
        action="store_true",
        help="Include hidden files and folders (default excludes dotfiles)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview actions without uploading")

    args = parser.parse_args()

    try:
        if args.remote_root and args.remote_parent_id is not None:
            raise ValueError("--remote-root and --remote-parent-id cannot be used together")

        result = upload_directory(
            args.local_dir,
            args.remote_root.strip("/"),
            args.remote_parent_id,
            args.dry_run,
            args.conflict_strategy,
            args.include_hidden,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
