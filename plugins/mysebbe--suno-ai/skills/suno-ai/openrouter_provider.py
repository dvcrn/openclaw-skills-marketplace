from __future__ import annotations

import asyncio
import base64
import json
import os
from contextlib import suppress
from pathlib import Path
from typing import List, TypeVar

import httpx
from pydantic import BaseModel

ResponseT = TypeVar("ResponseT", bound=BaseModel)
OPENCLAW_ENV = Path.home() / ".openclaw" / ".env"
DEFAULT_OPENROUTER_MODEL = "google/gemini-2.5-flash"


class OpenRouterProvider:
    def __init__(self, api_key: str, model: str):
        self._api_key = _load_openrouter_key() or api_key
        if not self._api_key:
            raise RuntimeError("OpenRouter API key is not available.")
        self._model = _normalize_model_name(model)
        self._response: dict | None = None

    async def generate_with_images(
        self,
        *,
        images: List[Path],
        response_schema: type[ResponseT],
        user_prompt: str | None = None,
        description: str | None = None,
        **kwargs,
    ) -> ResponseT:
        contents: list[dict] = []
        if user_prompt:
            contents.append({"type": "text", "text": user_prompt})
        for image in images:
            contents.append({"type": "image_url", "image_url": {"url": _image_to_data_url(image)}})

        messages: list[dict] = []
        if description:
            messages.append({"role": "system", "content": description})
        messages.append({"role": "user", "content": contents or [{"type": "text", "text": ""}]})

        payload = {
            "model": self._model,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", 512),
            "temperature": 0,
            "reasoning": {"exclude": True},
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": response_schema.__name__,
                    "strict": True,
                    "schema": response_schema.model_json_schema(),
                },
            },
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost",
                    "X-Title": "OpenClaw Suno Solver",
                },
                json=payload,
            )
            response.raise_for_status()
            self._response = response.json()

        parsed = _parse_json_content(_extract_message_content(self._response))
        return response_schema(**parsed)

    def cache_response(self, path: Path) -> None:
        if self._response is None:
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self._response, ensure_ascii=False, indent=2), encoding="utf-8")


class TileBinaryResponse(BaseModel):
    contains_target: bool


class PromptExtractionResponse(BaseModel):
    challenge_prompt: str


def has_openrouter_key() -> bool:
    return bool(_load_openrouter_key())


def install_hcaptcha_openrouter_patch() -> None:
    import hcaptcha_challenger.agent.challenger as challenger_module
    import hcaptcha_challenger.tools.internal.base as base_module
    import hcaptcha_challenger.tools.internal.providers.gemini as gemini_module

    if getattr(challenger_module, "_openclaw_openrouter_patch", False):
        return

    base_module.GeminiProvider = OpenRouterProvider
    gemini_module.GeminiProvider = OpenRouterProvider

    robotic_arm = challenger_module.RoboticArm
    original_init = robotic_arm.__init__
    original_challenge_image_label_binary = robotic_arm.challenge_image_label_binary

    def patched_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        self._checkbox_selector = (
            "//iframe[contains(@src, '/captcha/v1/') and "
            "(contains(@src, 'frame=checkbox') or contains(@src, 'frame=checkbox-invisible'))]"
        )
        self._challenge_selector = (
            "//iframe[contains(@src, '/captcha/v1/') and contains(@src, 'frame=challenge')]"
        )

    async def patched_get_challenge_frame_locator(self):
        candidate_frame = self._find_challenge_frame_recursive(self.page.main_frame, max_depth=4)
        if candidate_frame:
            with suppress(Exception):
                challenge_view = candidate_frame.locator("//div[@class='challenge-view']")
                if await challenge_view.is_visible(timeout=1000):
                    return candidate_frame

        with suppress(Exception):
            for frame in self.page.frames:
                if "/captcha/v1/" not in frame.url or "frame=challenge" not in frame.url:
                    continue
                challenge_view = frame.locator("//div[@class='challenge-view']")
                if await challenge_view.is_visible():
                    return frame
        return None

    def patched_find_challenge_frame_recursive(self, frame, current_depth=0, max_depth=4):
        if current_depth >= max_depth:
            return None
        for child_frame in frame.child_frames:
            if (
                not child_frame.child_frames
                and "/captcha/v1/" in child_frame.url
                and "frame=challenge" in child_frame.url
            ):
                return child_frame
            nested = patched_find_challenge_frame_recursive(
                self,
                child_frame,
                current_depth=current_depth + 1,
                max_depth=max_depth,
            )
            if nested is not None:
                return nested
        return None

    async def patched_challenge_image_label_binary(self):
        frame_challenge = await self.get_challenge_frame_locator()
        crumb_count = await self.check_crumb_count()
        cache_key = self.config.create_cache_key(self.captcha_payload)
        prompt = _extract_hcaptcha_prompt(self)

        for cid in range(crumb_count):
            await self._wait_for_all_loaders_complete()

            challenge_view = frame_challenge.locator("//div[@class='challenge-view']")
            challenge_screenshot = cache_key.joinpath(f"{cache_key.name}_{cid}_challenge_view.png")
            await challenge_view.screenshot(type="png", path=challenge_screenshot)
            if prompt.lower() in {"unknown", "select the tiles that match the challenge."}:
                prompt = await _infer_hcaptcha_prompt_from_image(
                    challenge_screenshot=challenge_screenshot,
                    model=self.config.IMAGE_CLASSIFIER_MODEL,
                    response_path=cache_key.joinpath(f"{cache_key.name}_{cid}_prompt_model_answer.json"),
                )

            task_xpath = "//div[@class='task' and contains(@aria-label, '{index}')]"
            selected_indexes: list[int] = []

            try:
                for index in range(9):
                    task_locator = frame_challenge.locator(task_xpath.format(index=index + 1))
                    tile_path = cache_key.joinpath(f"{cache_key.name}_{cid}_tile_{index + 1}.png")
                    await task_locator.screenshot(type="png", path=tile_path)
                    response_path = cache_key.joinpath(
                        f"{cache_key.name}_{cid}_tile_{index + 1}_model_answer.json"
                    )
                    should_click = await _classify_hcaptcha_tile(
                        tile_path=tile_path,
                        challenge_prompt=prompt,
                        model=self.config.IMAGE_CLASSIFIER_MODEL,
                        response_path=response_path,
                    )
                    if should_click:
                        selected_indexes.append(index + 1)
            except httpx.HTTPStatusError:
                raise
            except Exception:
                return await original_challenge_image_label_binary(self)

            if not selected_indexes:
                selected_indexes.append(1)

            challenger_module.logger.debug(
                f"[{cid+1}/{crumb_count}]TileClassifier prompt={prompt!r} selected={selected_indexes}"
            )

            for index in selected_indexes:
                task_locator = frame_challenge.locator(task_xpath.format(index=index))
                await self.click_by_mouse(task_locator)

            with suppress(Exception):
                submit_btn = frame_challenge.locator("//div[@class='button-submit button']")
                await self.click_by_mouse(submit_btn)

    robotic_arm.__init__ = patched_init
    robotic_arm.get_challenge_frame_locator = patched_get_challenge_frame_locator
    robotic_arm._find_challenge_frame_recursive = patched_find_challenge_frame_recursive
    robotic_arm.challenge_image_label_binary = patched_challenge_image_label_binary
    challenger_module._openclaw_openrouter_patch = True


def _load_openrouter_key() -> str:
    for name in ("OPENROUTER_API_KEY", "OPENCLAW_OPENROUTER_API_KEY"):
        value = os.environ.get(name)
        if value:
            return value
    if OPENCLAW_ENV.exists():
        for line in OPENCLAW_ENV.read_text(encoding="utf-8", errors="ignore").splitlines():
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            if key.strip() in {"OPENROUTER_API_KEY", "OPENCLAW_OPENROUTER_API_KEY"} and value.strip():
                return value.strip()
    return ""


def _normalize_model_name(model: str | None) -> str:
    if not model:
        return DEFAULT_OPENROUTER_MODEL
    if "/" in model:
        return model
    if model.startswith("gemini-"):
        return f"google/{model}"
    return model


async def _classify_hcaptcha_tile(
    *,
    tile_path: Path,
    challenge_prompt: str,
    model: str,
    response_path: Path,
) -> bool:
    last_error: Exception | None = None
    for candidate in _tile_candidate_models(model):
        for attempt in range(3):
            provider = OpenRouterProvider("", candidate)
            try:
                response = await provider.generate_with_images(
                    images=[tile_path],
                    response_schema=TileBinaryResponse,
                    user_prompt=_build_hcaptcha_tile_prompt(challenge_prompt),
                )
            except httpx.HTTPStatusError as exc:
                last_error = exc
                status_code = exc.response.status_code if exc.response is not None else None
                if status_code == 402:
                    break
                if status_code == 429 and attempt < 2:
                    await asyncio.sleep(3 * (attempt + 1))
                    continue
                raise
            provider.cache_response(response_path)
            return response.contains_target
    if last_error is not None:
        raise last_error
    raise RuntimeError("No candidate model available for hCaptcha tile classification.")


def _extract_hcaptcha_prompt(robotic_arm: object) -> str:
    captcha_payload = getattr(robotic_arm, "captcha_payload", None)
    if captcha_payload is not None:
        with suppress(Exception):
            prompt = captcha_payload.get_requester_question()
            if isinstance(prompt, str) and prompt.strip():
                return prompt.strip()
        with suppress(Exception):
            requester_question = getattr(captcha_payload, "requester_question", None)
            if isinstance(requester_question, dict):
                for value in requester_question.values():
                    if isinstance(value, str) and value.strip() and value.strip().lower() != "unknown":
                        return value.strip()
        with suppress(Exception):
            requester_question_example = getattr(captcha_payload, "requester_question_example", None)
            if isinstance(requester_question_example, list):
                for value in requester_question_example:
                    if isinstance(value, str) and value.strip() and value.strip().lower() != "unknown":
                        return value.strip()
    prompt = getattr(robotic_arm, "_challenge_prompt", "")
    if isinstance(prompt, str) and prompt.strip():
        return prompt.strip()
    return "Select the tiles that match the challenge."


def _build_hcaptcha_tile_prompt(challenge_prompt: str) -> str:
    lower_prompt = challenge_prompt.lower()
    if "human-made" in lower_prompt or "human made" in lower_prompt or "man-made" in lower_prompt:
        domain_hint = (
            "Human-made matches include machines, electronics, shelves, kiosks, signs, "
            "furniture, vehicles, and buildings. Natural objects like flowers, birds, fish, "
            "cacti, mountains, and scenery are not matches."
        )
    else:
        domain_hint = (
            "Decide only whether this single tile matches the target described in the prompt. "
            "If the tile is ambiguous or uncertain, prefer false."
        )
    return (
        "You are solving one tile from a 3x3 hCaptcha image challenge. "
        f'Original challenge prompt: "{challenge_prompt}". '
        "Determine whether THIS SINGLE TILE should be clicked. "
        f"{domain_hint} "
        'Return strict JSON with exactly one boolean field: {"contains_target": true|false}.'
    )


async def _infer_hcaptcha_prompt_from_image(
    *,
    challenge_screenshot: Path,
    model: str,
    response_path: Path,
) -> str:
    last_error: Exception | None = None
    for candidate in _tile_candidate_models(model):
        for attempt in range(3):
            provider = OpenRouterProvider("", candidate)
            try:
                response = await provider.generate_with_images(
                    images=[challenge_screenshot],
                    response_schema=PromptExtractionResponse,
                    user_prompt=(
                        "Read the instruction text at the top of this hCaptcha screenshot. "
                        "Return that instruction exactly as a short string in JSON. "
                        "Do not describe the images below it."
                    ),
                )
            except httpx.HTTPStatusError as exc:
                last_error = exc
                status_code = exc.response.status_code if exc.response is not None else None
                if status_code == 402:
                    break
                if status_code == 429 and attempt < 2:
                    await asyncio.sleep(3 * (attempt + 1))
                    continue
                raise
            provider.cache_response(response_path)
            prompt = response.challenge_prompt.strip()
            if prompt:
                return prompt
    if last_error is not None:
        raise last_error
    return "Select the tiles that match the challenge."


def _tile_candidate_models(model: str) -> list[str]:
    normalized = _normalize_model_name(model)
    candidates = [
        normalized,
        "google/gemini-2.5-flash-lite",
        "google/gemini-2.5-flash-lite-preview-09-2025",
        "google/gemini-2.5-flash",
    ]
    unique: list[str] = []
    for candidate in candidates:
        if candidate not in unique:
            unique.append(candidate)
    return unique


def _image_to_data_url(path: Path) -> str:
    suffix = path.suffix.lower()
    mime = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
    }.get(suffix, "image/png")
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def _extract_message_content(payload: dict) -> str:
    content = payload["choices"][0]["message"]["content"]
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        return "\n".join(part.get("text", "") for part in content if isinstance(part, dict)).strip()
    raise ValueError("OpenRouter returned an unexpected message format.")


def _parse_json_content(text: str) -> dict:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.startswith("json"):
            cleaned = cleaned[4:].strip()
    if not cleaned:
        raise json.JSONDecodeError("Empty content", text, 0)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(cleaned[start : end + 1])
        raise
