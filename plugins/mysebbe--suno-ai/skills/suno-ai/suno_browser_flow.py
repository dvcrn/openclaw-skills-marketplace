#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from playwright.async_api import Page as AsyncPage
from playwright.async_api import TimeoutError as PlaywrightTimeout
from playwright.async_api import async_playwright

from browser_session import (
    DEFAULT_COOKIE_FILE,
    DEFAULT_DEBUG_DIR,
    DEFAULT_PROFILE_DIR,
    DEFAULT_RAW_COOKIE_FILE,
    _setup_virtual_display_if_needed,
    load_cookie_records,
    save_cookie_records,
)
from openrouter_provider import has_openrouter_key, install_hcaptcha_openrouter_patch
from suno_auth import (
    SunoAuthError,
    authenticate_session,
    build_browser_session,
    load_cookie_bundle,
    save_cookie_header,
)

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUTPUT_DIR = SCRIPT_DIR.parent.parent / "output_mp3"
DEFAULT_DEBUG_LOG = DEFAULT_DEBUG_DIR / "latest_generate.log"
SUNO_API_BASE = "https://studio-api.prod.suno.com"
DEFAULT_TIMEOUT = 30
RECENT_FEED_LIMIT = 20


class DebugLogger:
    def __init__(self, path: Path, *, echo: bool = False):
        self.path = path.expanduser().resolve()
        self.echo = echo
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text("", encoding="utf-8")

    def log(self, message: str) -> None:
        line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}"
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
        if self.echo:
            print(line, flush=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate Suno tracks with a browser-backed flow and hCaptcha automation."
    )
    parser.add_argument("--prompt", help="Simple description prompt")
    parser.add_argument("--lyrics", help="Custom lyrics for advanced mode")
    parser.add_argument("--tags", help="Style tags for advanced mode")
    parser.add_argument("--title", help="Optional title")
    parser.add_argument(
        "--instrumental",
        action="store_true",
        help="Toggle instrumental mode in simple mode if the UI exposes it.",
    )
    parser.add_argument(
        "--wait-audio",
        action="store_true",
        help="Retained for compatibility. Browser generation always waits for audio.",
    )
    parser.add_argument(
        "--cookie-file",
        default=str(DEFAULT_COOKIE_FILE),
        help="Path to the normalized Suno cookie header file.",
    )
    parser.add_argument(
        "--raw-cookie-file",
        default=str(DEFAULT_RAW_COOKIE_FILE),
        help="Path to the raw Suno cookie JSON export.",
    )
    parser.add_argument(
        "--browser-profile",
        default=str(DEFAULT_PROFILE_DIR),
        help="Persistent Playwright profile directory for Suno.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory where generated MP3 files should be stored.",
    )
    parser.add_argument(
        "--import-cookies",
        help="Import cookies from a Netscape export, raw Cookie header, or JSON payload.",
    )
    parser.add_argument(
        "--validate-session",
        action="store_true",
        help="Validate the current cookies and print session details.",
    )
    parser.add_argument(
        "--credits-only",
        action="store_true",
        help="Print billing information instead of generating audio.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON output.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print step-by-step browser progress to stdout.",
    )
    parser.add_argument(
        "--max-attempts",
        type=int,
        default=8,
        help="How many full browser attempts to try before failing.",
    )
    return parser.parse_args()


def resolve_cookie_header(args: argparse.Namespace) -> tuple[str, dict]:
    cookie_path = Path(args.cookie_file).expanduser().resolve()
    source_path = (
        Path(args.import_cookies).expanduser().resolve() if args.import_cookies else cookie_path
    )

    if not source_path.exists():
        raise SunoAuthError(
            f"Cookie source not found: {source_path}. Export fresh Suno cookies first."
        )

    bundle = load_cookie_bundle(source_path)
    session = build_browser_session(bundle.header)
    session_info = authenticate_session(
        session,
        require_billing=args.validate_session or args.credits_only,
    )

    if args.import_cookies:
        save_cookie_header(cookie_path, bundle.header)

    result = {
        "cookie_file": str(cookie_path),
        "cookie_names": list(bundle.cookies.keys()),
        "cookie_source": str(source_path),
        "cookie_source_kind": bundle.source_kind,
        "session_id": session_info.session_id,
        "credits_left": session_info.credits_left,
        "billing": session_info.billing,
    }
    return bundle.header, result


def validate_generation_args(args: argparse.Namespace) -> None:
    has_simple = bool(args.prompt)
    has_advanced = bool(args.lyrics and args.tags)
    if has_simple and has_advanced:
        raise SunoAuthError("Use either --prompt or the pair --lyrics + --tags, not both.")
    if not has_simple and not has_advanced and not args.credits_only and not args.validate_session:
        raise SunoAuthError(
            "Nothing to do. Use --prompt, or --lyrics together with --tags, "
            "or run --validate-session / --credits-only."
        )


def print_result(payload: dict, *, as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, ensure_ascii=True, indent=2))
        return

    if "clips" in payload:
        print(f"Generated {len(payload['clips'])} clip(s).")
        for clip in payload["clips"]:
            print(f"- {clip.get('title') or 'Untitled'} [{clip.get('status')}]")
            print(f"  id: {clip.get('id')}")
            if clip.get("audio_url"):
                print(f"  audio: {clip['audio_url']}")
            if clip.get("file"):
                print(f"  file: {clip['file']}")
        if payload.get("debug_log"):
            print(f"Debug log: {payload['debug_log']}")
        return

    if payload.get("validated"):
        print("Suno session validated.")
        print(f"Cookie file: {payload['cookie_file']}")
        print(f"Cookie names: {', '.join(payload['cookie_names'])}")
        print(f"Session id: {payload['session_id']}")
        if payload.get("credits_left") is not None:
            print(f"Credits left: {payload['credits_left']}")
        return

    if "billing" in payload:
        billing = payload["billing"] or {}
        print(f"Credits left: {billing.get('total_credits_left') or billing.get('credits')}")
        if billing.get("monthly_limit") is not None:
            print(f"Monthly limit: {billing.get('monthly_limit')}")
        if billing.get("monthly_usage") is not None:
            print(f"Monthly usage: {billing.get('monthly_usage')}")


def run_browser_generation(args: argparse.Namespace) -> dict:
    logger = DebugLogger(DEFAULT_DEBUG_LOG, echo=args.verbose and not args.json)
    max_attempts = max(1, int(args.max_attempts or 1))
    last_exc: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        if attempt > 1:
            logger.log(f"Retrying full Suno browser attempt {attempt}/{max_attempts}.")
        session_meta = {
            "source": "persistent-profile",
            "credits_left": None,
        }
        try:
            payload = asyncio.run(_run_browser_generation_async(args, logger, session_meta))
            payload["debug_log"] = str(logger.path)
            payload["attempt"] = attempt
            return payload
        except SunoAuthError as exc:
            last_exc = exc
            logger.log(f"Browser attempt {attempt} failed: {exc}")
            if attempt >= max_attempts:
                raise
            time.sleep(2)
        except Exception as exc:
            last_exc = exc
            logger.log(f"Browser attempt {attempt} crashed: {exc}")
            if attempt >= max_attempts:
                raise SunoAuthError(f"Unexpected browser automation error: {exc}") from exc
            time.sleep(2)
    if last_exc is not None:
        if isinstance(last_exc, SunoAuthError):
            raise last_exc
        raise SunoAuthError(f"Unexpected browser automation error: {last_exc}") from last_exc
    raise SunoAuthError("Suno browser generation failed without a captured exception.")


def _prepare_browser_session(args: argparse.Namespace, logger: DebugLogger) -> dict:
    script_path = SCRIPT_DIR / "suno_login.py"
    command = [
        sys.executable,
        str(script_path),
        "--raw-cookie-file",
        str(Path(args.raw_cookie_file).expanduser().resolve()),
        "--profile-dir",
        str(Path(args.browser_profile).expanduser().resolve()),
        "--json",
    ]
    logger.log("Preparing persistent Suno browser session.")
    completed = subprocess.run(
        command,
        cwd=str(SCRIPT_DIR),
        capture_output=True,
        text=True,
        check=False,
    )
    stdout = completed.stdout.strip()
    stderr = completed.stderr.strip()
    if completed.returncode != 0:
        message = stdout or stderr or "suno_login.py failed without output."
        raise SunoAuthError(f"Failed to prepare Suno browser session: {message}")
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise SunoAuthError(f"Unexpected suno_login.py output: {stdout}") from exc
    if not payload.get("ok"):
        raise SunoAuthError(payload.get("error") or "Failed to prepare Suno browser session.")
    logger.log(
        "Prepared browser session: "
        f"source={payload.get('source')} credits={payload.get('credits_left')}"
    )
    return payload


async def _run_browser_generation_async(
    args: argparse.Namespace,
    logger: DebugLogger,
    session_meta: dict,
) -> dict:
    profile_dir = Path(args.browser_profile).expanduser().resolve()
    raw_cookie_file = Path(args.raw_cookie_file).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    response_tasks: set[asyncio.Task[Any]] = set()
    generated_clip_ids: list[str] = []
    recent_ids_cache: list[str] = []
    submission_state: dict[str, Any] = {
        "response_count": 0,
        "last_status": None,
        "last_url": None,
    }
    display = _setup_virtual_display_if_needed()
    try:
        async with async_playwright() as playwright:
            context = await playwright.chromium.launch_persistent_context(
                str(profile_dir),
                headless=False,
                viewport={"width": 1440, "height": 960},
                accept_downloads=True,
                ignore_default_args=["--enable-automation"],
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                ],
            )
            await context.add_init_script(
                """
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                if (!window.chrome) {
                  window.chrome = {};
                }
                if (!window.chrome.runtime) {
                  window.chrome.runtime = {};
                }
                """
            )
            def on_response(response: object) -> None:
                task = asyncio.create_task(
                    _handle_response_event(response, generated_clip_ids, logger, submission_state),
                    name="suno-response-handler",
                )
                response_tasks.add(task)
                task.add_done_callback(response_tasks.discard)

            context.on("response", on_response)
            page = await context.new_page()

            def on_console(message: object) -> None:
                task = asyncio.create_task(
                    _handle_console_event(message, logger),
                    name="suno-console-handler",
                )
                response_tasks.add(task)
                task.add_done_callback(response_tasks.discard)

            page.on("console", on_console)

            try:
                await _dismiss_popups(page)
                await page.goto("https://suno.com/create", wait_until="domcontentloaded", timeout=60000)
                await page.wait_for_timeout(5000)
                await _dismiss_popups(page)

                if "sign-in" in page.url:
                    restored = await _restore_session_from_raw_cookies(
                        context,
                        page,
                        raw_cookie_file,
                        logger,
                    )
                    if not restored:
                        raise SunoAuthError(
                            "Suno browser profile is not logged in. Re-import cookies and retry."
                        )
                    session_meta["source"] = "raw-cookie-file"

                token = await _fetch_clerk_token_async(page)
                baseline_feed = _fetch_recent_feed(token, limit=RECENT_FEED_LIMIT)
                baseline_ids = {
                    str(item.get("id"))
                    for item in baseline_feed
                    if isinstance(item, dict) and item.get("id")
                }
                logger.log(
                    f"Loaded baseline feed with {len(baseline_ids)} clip ids before generation."
                )

                if args.lyrics and args.tags:
                    await _prepare_advanced_song(
                        page,
                        args.lyrics,
                        args.tags,
                        args.title or "OpenClaw Song",
                    )
                else:
                    await _prepare_simple_song(
                        page,
                        args.prompt or "",
                        title=args.title,
                        instrumental=args.instrumental,
                    )

                started_at = time.time()
                await _save_debug_screenshot(page, logger, "before_create.png")
                await _click_create(page, logger)

                async def recent_clip_detector() -> list[str]:
                    nonlocal recent_ids_cache
                    current_token = await _fetch_clerk_token_async(page)
                    recent_items = _fetch_recent_feed(current_token, limit=RECENT_FEED_LIMIT)
                    recent_ids_cache = _detect_recent_clip_ids(
                        recent_items,
                        baseline_ids=baseline_ids,
                        created_after=started_at,
                        expected_title=args.title,
                        expected_prompt=args.prompt or "",
                    )
                    return recent_ids_cache

                await _wait_for_submission(
                    page,
                    generated_clip_ids,
                    logger,
                    recent_clip_detector=recent_clip_detector,
                    submission_state=submission_state,
                )

                if not generated_clip_ids:
                    generated_clip_ids.extend(recent_ids_cache)
                if not generated_clip_ids:
                    current_token = await _fetch_clerk_token_async(page)
                    generated_clip_ids.extend(
                        _detect_recent_clip_ids(
                            _fetch_recent_feed(current_token, limit=RECENT_FEED_LIMIT),
                            baseline_ids=baseline_ids,
                            created_after=started_at,
                            expected_title=args.title,
                            expected_prompt=args.prompt or "",
                        )
                    )
                if not generated_clip_ids:
                    raise SunoAuthError(
                        "Suno did not expose new clip ids after submission. "
                        f"See {logger.path} for the browser trace."
                    )

                clip_ids = _dedupe_clip_ids(generated_clip_ids)
                logger.log(f"Tracking clip ids: {clip_ids}")
                clips = await _poll_for_clips(page, clip_ids, logger)

                for clip in clips:
                    audio_url = clip.get("audio_url")
                    clip_id = clip.get("id")
                    if audio_url and clip_id:
                        clip["file"] = str(_download_audio(audio_url, clip, output_dir))

                await _persist_async_context_cookies(context, raw_cookie_file)
                billing = _fetch_billing(await _fetch_clerk_token_async(page))
                return {
                    "cookie_source": session_meta.get("source"),
                    "clips": clips,
                    "billing": billing,
                }
            finally:
                if response_tasks:
                    await asyncio.gather(*response_tasks, return_exceptions=True)
                await context.close()
    finally:
        if display is not None:
            display.stop()


async def _handle_response_event(
    response: object,
    generated_clip_ids: list[str],
    logger: DebugLogger,
    submission_state: dict[str, Any],
) -> None:
    try:
        url = response.url
        method = response.request.method
        status = response.status
    except Exception:
        return

    if method == "POST" and "/api/generate/" in url:
        submission_state["response_count"] = int(submission_state.get("response_count") or 0) + 1
        submission_state["last_status"] = status
        submission_state["last_url"] = url
        logger.log(f"Observed generation response: {status} {url}")
        if status >= 400:
            try:
                headers = dict(response.headers)
                interesting_headers = {
                    key: value
                    for key, value in headers.items()
                    if key.lower()
                    in {
                        "content-type",
                        "content-length",
                        "server",
                        "cf-ray",
                        "x-request-id",
                        "x-trace-id",
                        "x-amz-cf-id",
                        "x-cache",
                        "via",
                    }
                }
                if interesting_headers:
                    logger.log(
                        f"Generation response headers: {json.dumps(interesting_headers, ensure_ascii=True)}"
                    )
            except Exception as exc:
                logger.log(f"Failed to inspect generation response headers: {exc}")
        try:
            post_data = response.request.post_data or ""
            if post_data:
                try:
                    parsed_request = json.loads(post_data)
                except Exception:
                    logger.log(f"Generation request body preview: {post_data[:400]}")
                else:
                    request_keys = sorted(parsed_request.keys())
                    logger.log(f"Generation request keys: {request_keys}")
                    interesting_keys = [
                        key for key in request_keys if "captcha" in key.lower() or "token" in key.lower()
                    ]
                    if interesting_keys:
                        logger.log(f"Generation request auth-related keys: {interesting_keys}")
                    token_value = parsed_request.get("token")
                    if isinstance(token_value, str) and token_value:
                        logger.log(
                            "Generation request token fingerprint: "
                            f"len={len(token_value)} sha256={hashlib.sha256(token_value.encode('utf-8')).hexdigest()[:16]}"
                        )
        except Exception as exc:
            logger.log(f"Failed to inspect generation request body: {exc}")
        try:
            payload = await response.json()
        except Exception as exc:
            logger.log(f"Failed to decode generation response JSON: {exc}")
            try:
                body = await response.text()
                if body:
                    logger.log(f"Generation response text: {body[:400]}")
            except Exception as text_exc:
                logger.log(f"Failed to read generation response text: {text_exc}")
            return
        clip_ids = _extract_clip_ids(payload)
        if clip_ids:
            for clip_id in clip_ids:
                if clip_id not in generated_clip_ids:
                    generated_clip_ids.append(clip_id)
            logger.log(f"Captured clip ids from generation response: {clip_ids}")
        else:
            logger.log(f"Generation response did not contain clip ids: {json.dumps(payload)[:400]}")


async def _handle_console_event(message: object, logger: DebugLogger) -> None:
    try:
        text = message.text
    except Exception:
        return
    try:
        message_type = message.type
    except Exception:
        message_type = ""
    if text == "captcha required, awaiting verification":
        logger.log("Browser console: captcha required, awaiting verification")
        return
    if text != "captcha verified":
        if message_type != "error":
            return
        try:
            args = message.args or []
        except Exception:
            args = []
        if args:
            try:
                payload = await args[0].json_value()
            except Exception:
                logger.log(f"Browser console error: {text[:400]}")
                return
            if isinstance(payload, (dict, list, str, int, float, bool)) or payload is None:
                rendered = json.dumps(payload, ensure_ascii=True, default=str)
            else:
                rendered = str(payload)
            logger.log(f"Browser console error payload: {rendered[:400]}")
            return
        logger.log(f"Browser console error: {text[:400]}")
        return
    try:
        args = message.args or []
    except Exception:
        args = []
    if len(args) < 2:
        logger.log("Browser console: captcha verified (without token payload)")
        return
    try:
        token_value = await args[1].json_value()
    except Exception as exc:
        logger.log(f"Failed to inspect browser captcha token: {exc}")
        return
    if isinstance(token_value, str) and token_value:
        logger.log(
            "Browser captcha token fingerprint: "
            f"len={len(token_value)} sha256={hashlib.sha256(token_value.encode('utf-8')).hexdigest()[:16]}"
        )
        return
    logger.log(f"Browser console: captcha verified payload type={type(token_value).__name__}")


async def _dismiss_popups(page: AsyncPage) -> None:
    for label in ("Not now", "Skip", "Maybe later", "Close"):
        try:
            button = page.locator(f"button:has-text('{label}')").first
            if await button.is_visible(timeout=500):
                await button.click(timeout=1000)
                await page.wait_for_timeout(500)
        except Exception:
            continue
    try:
        await page.keyboard.press("Escape")
    except Exception:
        pass


async def _prepare_simple_song(
    page: AsyncPage,
    prompt: str,
    *,
    title: str | None,
    instrumental: bool,
) -> None:
    await _click_first_visible(
        page,
        [
            "button:has-text('Simple')",
            "[role='button']:has-text('Simple')",
        ],
    )
    await page.wait_for_timeout(1000)
    visible_textareas = await _visible_textareas(page)
    textarea = visible_textareas[0] if visible_textareas else None
    if textarea is None:
        raise SunoAuthError("Unable to find the Suno description textarea.")
    await _fill_textarea(textarea, prompt)
    if title:
        await _fill_title(page, title)
    if instrumental:
        await _enable_instrumental(page)


async def _prepare_advanced_song(
    page: AsyncPage,
    lyrics: str,
    tags: str,
    title: str,
) -> None:
    await _click_first_visible(
        page,
        [
            "button:has-text('Advanced')",
            "[role='tab']:has-text('Advanced')",
            "[role='button']:has-text('Advanced')",
        ],
        required=True,
    )
    await page.wait_for_timeout(2000)

    visible_textareas = await _visible_textareas(page)
    if len(visible_textareas) < 2:
        raise SunoAuthError("Unable to find the Suno advanced-mode textareas.")

    await _fill_textarea(visible_textareas[0], lyrics)
    await _fill_textarea(visible_textareas[1], tags)
    await _fill_title(page, title)


async def _fill_title(page: AsyncPage, title: str) -> None:
    for selector in (
        "input[placeholder*='Title']",
        "input[placeholder*='title']",
        "input[placeholder*='Song']",
        "input[name*='title']",
    ):
        try:
            field = page.locator(selector).first
            if await field.is_visible(timeout=500):
                await field.click(timeout=1000)
                await field.fill("")
                await field.fill(title)
                return
        except Exception:
            continue


async def _enable_instrumental(page: AsyncPage) -> None:
    for selector in (
        "button:has-text('Instrumental')",
        "[role='switch']:has-text('Instrumental')",
        "label:has-text('Instrumental')",
    ):
        try:
            control = page.locator(selector).first
            if not await control.is_visible(timeout=500):
                continue
            state = (
                await control.get_attribute("aria-pressed")
                or await control.get_attribute("aria-checked")
                or await control.get_attribute("data-state")
                or ""
            ).lower()
            if state in {"true", "checked", "on"}:
                return
            await control.click(timeout=1000)
            await page.wait_for_timeout(500)
            return
        except Exception:
            continue


async def _click_create(page: AsyncPage, logger: DebugLogger, *, force: bool = False) -> None:
    buttons = page.locator("button")
    count = await buttons.count()
    chosen = None
    chosen_y = -1.0
    for index in range(count):
        button = buttons.nth(index)
        try:
            text = ((await button.text_content()) or "").strip().lower()
            if "create" not in text or not await button.is_visible(timeout=500):
                continue
            box = await button.bounding_box() or {}
            y = float(box.get("y") or 0.0)
            if y >= chosen_y:
                chosen = button
                chosen_y = y
        except Exception:
            continue

    if chosen is None:
        raise SunoAuthError("Unable to find the Suno Create button.")
    if force:
        try:
            await chosen.click(timeout=3000, force=True)
        except Exception:
            handle = await chosen.element_handle()
            if handle is None:
                raise
            await page.evaluate("(button) => button.click()", handle)
        logger.log("Clicked Suno Create button with force.")
        return
    await chosen.click(timeout=3000)
    logger.log("Clicked Suno Create button.")


async def _wait_for_submission(
    page: AsyncPage,
    generated_clip_ids: list[str],
    logger: DebugLogger,
    *,
    recent_clip_detector: Any,
    submission_state: dict[str, Any],
) -> None:
    saw_captcha = False
    captcha_solved = False
    retried_after_captcha = False
    retried_without_captcha = False
    captcha_attempts = 0
    captcha_resubmit_count = 0
    last_resubmit_at = 0.0
    response_count_at_last_resubmit = -1
    deadline = time.time() + 150
    next_feed_check = 0.0

    while time.time() < deadline:
        if generated_clip_ids:
            return

        now = time.time()
        if now >= next_feed_check:
            next_feed_check = now + 5
            recent_ids = await recent_clip_detector()
            if recent_ids:
                for clip_id in recent_ids:
                    if clip_id not in generated_clip_ids:
                        generated_clip_ids.append(clip_id)
                logger.log(f"Recovered clip ids from recent feed fallback: {recent_ids}")
                return

        captcha_frames = await _visible_captcha_frames(page)
        if captcha_frames:
            if not saw_captcha:
                logger.log(f"hCaptcha appeared with {len(captcha_frames)} visible frame(s).")
            saw_captcha = True
            if not captcha_solved:
                captcha_attempts += 1
                await _click_hcaptcha_checkbox_if_present(page, logger)
                captcha_solved = await _solve_hcaptcha_if_needed(page, logger)
                if not captcha_solved:
                    logger.log(f"hCaptcha solver attempt {captcha_attempts} did not complete cleanly.")
                    if captcha_attempts >= 3:
                        await _save_debug_screenshot(page, logger, "captcha_solver_failed.png")
                        raise SunoAuthError(
                            "Suno hCaptcha solver did not complete cleanly after multiple attempts. "
                            f"See {logger.path}."
                        )
                    await page.wait_for_timeout(2000)
                    continue
                captcha_cleared = await _wait_for_captcha_to_clear(page, logger)
                if not captcha_cleared:
                    logger.log(
                        f"hCaptcha remained visible after solver attempt {captcha_attempts}."
                    )
                    status = submission_state.get("last_status")
                    if status == 403 and captcha_resubmit_count < 3 and await _is_create_ready(page):
                        await _click_create(page, logger, force=True)
                        captcha_resubmit_count += 1
                        last_resubmit_at = time.time()
                        response_count_at_last_resubmit = int(
                            submission_state.get("response_count") or 0
                        )
                        submission_state["last_status"] = None
                        logger.log(
                            "Retried Create after captcha success while the iframe was still visible "
                            f"and Suno had returned 403. attempt={captcha_resubmit_count}/3"
                        )
                        deadline = time.time() + 60
                        await page.wait_for_timeout(1500)
                        continue
                    if status == 403 and captcha_attempts < 3:
                        logger.log("Suno returned 403 while the captcha iframe stayed visible. Retrying captcha.")
                        captcha_solved = False
                        await page.wait_for_timeout(2000)
                        continue
                    logger.log("Waiting for Suno to settle before treating the captcha as stuck.")
                    deadline = time.time() + 45
                    continue
                deadline = time.time() + 120
                continue
            if (
                captcha_resubmit_count > 0
                and captcha_resubmit_count < 3
                and time.time() - last_resubmit_at >= 8
                and int(submission_state.get("response_count") or 0) == response_count_at_last_resubmit
                and await _is_create_ready(page)
            ):
                await _click_create(page, logger, force=True)
                captcha_resubmit_count += 1
                last_resubmit_at = time.time()
                response_count_at_last_resubmit = int(submission_state.get("response_count") or 0)
                submission_state["last_status"] = None
                logger.log(
                    "No new generation response arrived after the previous captcha re-submit. "
                    f"Trying Create again ({captcha_resubmit_count}/3)."
                )
                deadline = time.time() + 45
                await page.wait_for_timeout(1500)
                continue
            if submission_state.get("last_status") == 403 and captcha_attempts < 3:
                if captcha_resubmit_count < 3 and await _is_create_ready(page):
                    await _click_create(page, logger, force=True)
                    captcha_resubmit_count += 1
                    last_resubmit_at = time.time()
                    response_count_at_last_resubmit = int(submission_state.get("response_count") or 0)
                    submission_state["last_status"] = None
                    logger.log(
                        "Retried Create while the captcha iframe was still present after a Suno 403. "
                        f"attempt={captcha_resubmit_count}/3"
                    )
                    deadline = time.time() + 60
                    await page.wait_for_timeout(1500)
                    continue
                logger.log("Suno returned 403 after captcha. Retrying captcha while the iframe is still present.")
                captcha_solved = False
                await page.wait_for_timeout(1500)
                continue
        elif saw_captcha and captcha_solved and not retried_after_captcha:
            recent_ids = await recent_clip_detector()
            if recent_ids:
                for clip_id in recent_ids:
                    if clip_id not in generated_clip_ids:
                        generated_clip_ids.append(clip_id)
                logger.log(f"Recovered clip ids immediately after captcha: {recent_ids}")
                return
            if await _is_create_ready(page):
                await _click_create(page, logger)
                retried_after_captcha = True
                status = submission_state.get("last_status")
                if status == 403:
                    logger.log("Retried Create after captcha success and Suno 403 response.")
                else:
                    logger.log("Retried Create after captcha success.")
                deadline = time.time() + 90
        elif not saw_captcha and not retried_without_captcha and now + 120 > deadline:
            if await _is_create_ready(page):
                await _click_create(page, logger)
                retried_without_captcha = True
                logger.log("Retried Create after no generation response appeared.")
                deadline = time.time() + 60

        await page.wait_for_timeout(1000)

    await _save_debug_screenshot(page, logger, "submit_timeout.png")
    if saw_captcha:
        raise SunoAuthError(
            "Suno did not submit a generation request after the captcha flow. "
            f"See {logger.path}."
        )
    raise SunoAuthError(
        "Suno did not submit a generation request after clicking Create. "
        f"See {logger.path}."
    )


async def _click_hcaptcha_checkbox_if_present(page: AsyncPage, logger: DebugLogger) -> None:
    for frame in page.frames:
        url = frame.url or ""
        if "/captcha/v1/" not in url or "frame=checkbox" not in url:
            continue
        for selector in ("#checkbox", "div[role='checkbox']", "body"):
            try:
                locator = frame.locator(selector).first
                if await locator.is_visible(timeout=1500):
                    await locator.click(timeout=3000)
                    logger.log(f"Clicked hCaptcha checkbox using selector {selector}.")
                    await page.wait_for_timeout(2500)
                    return
            except Exception:
                continue


async def _solve_hcaptcha_if_needed(page: AsyncPage, logger: DebugLogger) -> bool:
    if not has_openrouter_key():
        raise SunoAuthError("OpenRouter API key is required to solve Suno hCaptcha.")

    try:
        from loguru import logger as loguru_logger

        loguru_logger.remove()
    except Exception:
        pass

    try:
        install_hcaptcha_openrouter_patch()
        from hcaptcha_challenger import AgentConfig, AgentV
    except Exception as exc:
        raise SunoAuthError(f"Failed to initialize hCaptcha solver: {exc}") from exc

    logger.log("Starting hCaptcha solver.")
    agent = AgentV(
        page=page,
        agent_config=AgentConfig(
            GEMINI_API_KEY="openrouter-bridge",
            CHALLENGE_CLASSIFIER_MODEL="gemini-2.5-flash",
            IMAGE_CLASSIFIER_MODEL="gemini-2.5-flash",
            SPATIAL_POINT_REASONER_MODEL="gemini-2.5-flash",
            SPATIAL_PATH_REASONER_MODEL="gemini-2.5-flash",
            RESPONSE_TIMEOUT=60,
            EXECUTION_TIMEOUT=180,
            WAIT_FOR_CHALLENGE_VIEW_TO_RENDER_MS=2500,
            enable_challenger_debug=False,
        ),
    )
    try:
        signal = await agent.wait_for_challenge()
    except Exception as exc:
        frames = await _visible_captcha_frames(page)
        if not frames:
            logger.log("hCaptcha solver lost the frame, but captcha is no longer visible.")
            return True
        if "NoneType" in str(exc) and "locator" in str(exc):
            logger.log("hCaptcha solver hit a transient frame race. Retrying solver flow.")
            return False
        raise SunoAuthError(f"hCaptcha solving failed: {exc}") from exc

    logger.log(f"hCaptcha solver finished with signal: {signal}")
    if getattr(signal, "name", str(signal)) == "SUCCESS" or "SUCCESS" in str(signal):
        try:
            captcha_responses = getattr(agent, "cr_list", []) or []
            if captcha_responses:
                last_response = captcha_responses[-1]
                generated_pass_uuid = getattr(last_response, "generated_pass_UUID", "")
                if isinstance(generated_pass_uuid, str) and generated_pass_uuid:
                    logger.log(
                        "hCaptcha pass fingerprint: "
                        f"len={len(generated_pass_uuid)} "
                        f"sha256={hashlib.sha256(generated_pass_uuid.encode('utf-8')).hexdigest()[:16]}"
                    )
        except Exception as exc:
            logger.log(f"Failed to inspect hCaptcha pass token: {exc}")
        return True
    raise SunoAuthError(f"hCaptcha solving ended with signal: {signal}")


async def _wait_for_captcha_to_clear(page: AsyncPage, logger: DebugLogger) -> bool:
    for _ in range(15):
        frames = await _visible_captcha_frames(page)
        if not frames:
            logger.log("hCaptcha frames cleared from the page.")
            return True
        await page.wait_for_timeout(1000)
    logger.log("hCaptcha frames still visible after solver completed.")
    return False


async def _visible_captcha_frames(page: AsyncPage) -> list[dict[str, Any]]:
    return await page.evaluate(
        """
        () => Array.from(document.querySelectorAll('iframe'))
          .filter((frame) => {
            const src = frame.src || '';
            return src.includes('/captcha/v1/') && frame.offsetHeight > 0 && frame.offsetWidth > 0;
          })
          .map((frame) => ({
            src: frame.src || '',
            width: frame.offsetWidth,
            height: frame.offsetHeight,
          }))
        """
    )


async def _is_create_ready(page: AsyncPage) -> bool:
    buttons = page.locator("button")
    count = await buttons.count()
    for index in range(count):
        button = buttons.nth(index)
        try:
            text = ((await button.text_content()) or "").strip().lower()
            if "create" not in text or not await button.is_visible(timeout=500):
                continue
            disabled = await button.get_attribute("disabled")
            aria_disabled = (await button.get_attribute("aria-disabled") or "").lower()
            return disabled is None and aria_disabled != "true"
        except Exception:
            continue
    return False


async def _poll_for_clips(
    page: AsyncPage,
    clip_ids: list[str],
    logger: DebugLogger,
) -> list[dict]:
    pending = set(clip_ids)
    finished: dict[str, dict] = {}
    deadline = time.time() + 300

    while pending and time.time() < deadline:
        token = await _fetch_clerk_token_async(page)
        items = _fetch_feed_by_ids(token, clip_ids)
        for item in items:
            clip_id = str(item.get("id") or "")
            status = item.get("status")
            if not clip_id or clip_id not in pending:
                continue
            if status in {"complete", "streaming"} and item.get("audio_url"):
                finished[clip_id] = item
                pending.remove(clip_id)
            elif status == "error":
                finished[clip_id] = item
                pending.remove(clip_id)
        if pending:
            status_text = ", ".join(
                f"{item.get('id')}={item.get('status')}"
                for item in items
                if item.get("id") in pending
            )
            logger.log(f"Waiting for clips: {status_text or ', '.join(sorted(pending))}")
            await page.wait_for_timeout(5000)

    if pending:
        raise SunoAuthError(f"Suno generation timed out for clip ids: {', '.join(sorted(pending))}")
    return [finished[clip_id] for clip_id in clip_ids if clip_id in finished]


async def _fetch_clerk_token_async(page: AsyncPage) -> str:
    try:
        await page.wait_for_function(
            "() => Boolean(window.Clerk && window.Clerk.session)",
            timeout=20000,
        )
    except PlaywrightTimeout as exc:
        raise SunoAuthError("Clerk session is not available in the Suno browser context.") from exc

    token = await page.evaluate(
        """
        async () => {
          if (!window.Clerk || !window.Clerk.session) {
            return null;
          }
          return await window.Clerk.session.getToken();
        }
        """
    )
    if not token:
        raise SunoAuthError("Failed to obtain a Suno Clerk token from the browser session.")
    return token


def _fetch_billing(token: str) -> dict:
    response = requests.get(
        f"{SUNO_API_BASE}/api/billing/info/",
        headers=_api_headers(token),
        timeout=DEFAULT_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()


def _fetch_recent_feed(token: str, *, limit: int) -> list[dict]:
    response = requests.get(
        f"{SUNO_API_BASE}/api/feed/?limit={limit}",
        headers=_api_headers(token),
        timeout=DEFAULT_TIMEOUT,
    )
    response.raise_for_status()
    payload = response.json()
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        clips = payload.get("clips") or payload.get("items") or []
        return [item for item in clips if isinstance(item, dict)]
    return []


def _fetch_feed_by_ids(token: str, clip_ids: list[str]) -> list[dict]:
    response = requests.get(
        f"{SUNO_API_BASE}/api/feed/?ids={','.join(clip_ids)}",
        headers=_api_headers(token),
        timeout=DEFAULT_TIMEOUT,
    )
    response.raise_for_status()
    payload = response.json()
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        clips = payload.get("clips") or payload.get("items") or []
        return [item for item in clips if isinstance(item, dict)]
    return []


def _detect_recent_clip_ids(
    items: list[dict],
    *,
    baseline_ids: set[str],
    created_after: float,
    expected_title: str | None,
    expected_prompt: str,
) -> list[str]:
    candidates = [
        item
        for item in items
        if str(item.get("id") or "") not in baseline_ids
        and _parse_suno_timestamp(item.get("created_at")) >= created_after - 120
    ]
    if expected_title:
        title_matches = [
            item for item in candidates if (item.get("title") or "").strip() == expected_title.strip()
        ]
        if title_matches:
            candidates = title_matches
    prompt_probe = _normalize_prompt_probe(expected_prompt)
    if prompt_probe:
        prompt_matches = []
        for item in candidates:
            metadata = item.get("metadata") or {}
            prompt_text = str(metadata.get("prompt") or "")
            if prompt_probe in _normalize_prompt_probe(prompt_text):
                prompt_matches.append(item)
        if prompt_matches:
            candidates = prompt_matches

    candidates.sort(key=lambda item: _parse_suno_timestamp(item.get("created_at")), reverse=True)
    return _dedupe_clip_ids([str(item.get("id")) for item in candidates if item.get("id")])[:2]


def _api_headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Origin": "https://suno.com",
        "Referer": "https://suno.com/",
    }


def _extract_clip_ids(payload: object) -> list[str]:
    items: list[dict] = []
    if isinstance(payload, dict):
        clips = payload.get("clips")
        if isinstance(clips, list):
            items = [clip for clip in clips if isinstance(clip, dict)]
    elif isinstance(payload, list):
        items = [clip for clip in payload if isinstance(clip, dict)]
    return _dedupe_clip_ids([str(item.get("id")) for item in items if item.get("id")])


def _dedupe_clip_ids(items: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for item in items:
        if not item or item in seen:
            continue
        seen.add(item)
        deduped.append(item)
    return deduped


def _download_audio(audio_url: str, clip: dict, output_dir: Path) -> Path:
    response = requests.get(audio_url, stream=True, timeout=120)
    response.raise_for_status()
    title = clip.get("title") or "suno-track"
    clip_id = clip.get("id") or "clip"
    safe_title = re.sub(r"[^A-Za-z0-9._-]+", "_", title).strip("_") or "suno-track"
    target = output_dir / f"{safe_title}_{clip_id[:8]}.mp3"
    with target.open("wb") as handle:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                handle.write(chunk)
    return target


def _parse_suno_timestamp(value: object) -> float:
    if not value:
        return 0.0
    try:
        text = str(value).replace("Z", "+00:00")
        return datetime.fromisoformat(text).timestamp()
    except Exception:
        return 0.0


def _normalize_prompt_probe(value: str) -> str:
    lowered = value.strip().lower()
    return re.sub(r"[^a-z0-9]+", " ", lowered).strip()


async def _visible_textareas(page: AsyncPage) -> list[Any]:
    textareas = page.locator("textarea")
    count = await textareas.count()
    visible: list[Any] = []
    for index in range(count):
        candidate = textareas.nth(index)
        try:
            if await candidate.is_visible():
                visible.append(candidate)
        except Exception:
            continue
    return visible


async def _restore_session_from_raw_cookies(
    context: Any,
    page: AsyncPage,
    raw_cookie_file: Path,
    logger: DebugLogger,
) -> bool:
    if not raw_cookie_file.exists():
        logger.log(f"Raw cookie file not found for session restore: {raw_cookie_file}")
        return False

    cookies = load_cookie_records(raw_cookie_file)
    await context.clear_cookies()
    await context.add_cookies(cookies)
    await page.goto("https://suno.com/create", wait_until="domcontentloaded", timeout=60000)
    await page.wait_for_timeout(4000)
    await _dismiss_popups(page)
    if "sign-in" in page.url:
        logger.log("Raw cookie import did not restore a logged-in Suno session.")
        return False
    logger.log("Restored Suno browser session from raw cookie file.")
    await _persist_async_context_cookies(context, raw_cookie_file)
    return True


async def _persist_async_context_cookies(context: Any, raw_cookie_file: Path) -> None:
    cookies = [
        cookie
        for cookie in await context.cookies()
        if "suno.com" in str(cookie.get("domain") or "")
    ]
    if cookies:
        save_cookie_records(raw_cookie_file, cookies)


async def _fill_textarea(locator: Any, text: str) -> None:
    await locator.click(timeout=1000)
    await locator.fill("")
    await locator.fill(text)


async def _click_first_visible(
    page: AsyncPage,
    selectors: list[str],
    *,
    required: bool = False,
) -> bool:
    for selector in selectors:
        try:
            candidate = page.locator(selector).first
            if await candidate.is_visible(timeout=500):
                await candidate.click(timeout=1000)
                return True
        except Exception:
            continue
    if required:
        raise SunoAuthError(f"Unable to find a visible control for selectors: {selectors}")
    return False


async def _save_debug_screenshot(page: AsyncPage, logger: DebugLogger, filename: str) -> None:
    target = logger.path.parent / filename
    try:
        await page.screenshot(path=str(target))
        logger.log(f"Saved screenshot: {target}")
    except Exception as exc:
        logger.log(f"Failed to save screenshot {target}: {exc}")


def main() -> int:
    args = parse_args()
    validate_generation_args(args)

    try:
        if args.validate_session or args.credits_only:
            _, session_meta = resolve_cookie_header(args)
            if args.validate_session and not args.prompt and not args.lyrics and not args.credits_only:
                print_result({"validated": True, **session_meta}, as_json=args.json)
                return 0
            if args.credits_only and not args.prompt and not args.lyrics:
                print_result({"billing": session_meta["billing"]}, as_json=args.json)
                return 0

        payload = run_browser_generation(args)
        print_result(payload, as_json=args.json)
        return 0
    except SunoAuthError as exc:
        if args.json:
            print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=True, indent=2))
        else:
            print(f"Error: {exc}")
        return 1
    except requests.HTTPError as exc:
        message = exc.response.text if exc.response is not None else str(exc)
        if args.json:
            print(json.dumps({"ok": False, "error": message}, ensure_ascii=True, indent=2))
        else:
            print(f"Error: {message}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
