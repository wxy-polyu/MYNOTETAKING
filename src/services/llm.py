import json
import os
import urllib.error
import urllib.request
from typing import Optional

DEEPSEEK_API_BASE = os.environ.get("DEEPSEEK_API_BASE", "https://api.deepseek.com").rstrip("/")
DEEPSEEK_MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")
MAX_TEXT_LENGTH = 8000

LANGUAGE_LABELS = {
    "en": "English",
    "zh-CN": "Simplified Chinese",
    "zh-TW": "Traditional Chinese",
    "ja": "Japanese",
    "ko": "Korean",
    "fr": "French",
    "de": "German",
    "es": "Spanish",
}


def translate_text(text: str, target_language: str, source_language: Optional[str] = None) -> str:
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("DEEPSEEK_API_KEY is not configured")

    text = (text or "").strip()
    if not text:
        raise ValueError("Text is required")
    if len(text) > MAX_TEXT_LENGTH:
        raise ValueError(f"Text exceeds maximum length of {MAX_TEXT_LENGTH} characters")

    target_label = LANGUAGE_LABELS.get(target_language, target_language)
    source_hint = ""
    if source_language and source_language != "auto":
        source_label = LANGUAGE_LABELS.get(source_language, source_language)
        source_hint = f" from {source_label}"

    system_prompt = (
        "You are a professional translator. Translate the user's text accurately. "
        "Preserve meaning, tone, and formatting (line breaks, lists). "
        "Output only the translation with no explanations or quotes."
    )
    user_prompt = f"Translate the following text{source_hint} into {target_label}:\n\n{text}"

    url = f"{DEEPSEEK_API_BASE}/chat/completions"
    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.3,
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            raw = response.read().decode("utf-8")
            status = response.status
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"DeepSeek API error ({e.code}): {detail}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"DeepSeek API request failed: {e.reason}")

    if status != 200:
        raise RuntimeError(f"DeepSeek API error ({status}): {raw[:500]}")

    data = json.loads(raw)
    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        raise RuntimeError("Unexpected response from DeepSeek API")

    return (content or "").strip()
