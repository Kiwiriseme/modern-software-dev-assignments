import base64
import hashlib
import json
import logging
import re

import requests
from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.db import transaction

from notes.models import AISettings, Todo

logger = logging.getLogger(__name__)

# ── Encryption ──────────────────────────────────────────────────────────────


def _get_fernet():
    """Derive a Fernet-compatible key from Django's SECRET_KEY."""
    key = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
    return Fernet(base64.urlsafe_b64encode(key))


def encrypt_api_key(plaintext: str) -> str:
    """Encrypt an API key for database storage."""
    if not plaintext:
        return ""
    f = _get_fernet()
    return f.encrypt(plaintext.encode()).decode()


def decrypt_api_key(ciphertext: str) -> str:
    """Decrypt an API key from database storage."""
    if not ciphertext:
        return ""
    f = _get_fernet()
    try:
        return f.decrypt(ciphertext.encode()).decode()
    except InvalidToken:
        logger.warning("Failed to decrypt stored API key (invalid token)")
        return ""


# ── AI System Prompt ────────────────────────────────────────────────────────

SYSTEM_PROMPT = (
    "你是一个任务提取助手。请分析以下笔记内容，提取其中隐含的待办事项。"
    "每个待办事项应该是一个具体可执行的任务。"
    "以 JSON 数组格式返回，每个元素包含 title 字段。"
    "如果没有待办事项，返回空数组 []。"
)


# ── AI API Call ─────────────────────────────────────────────────────────────


def call_ai_api(ai_settings: AISettings, note_content: str):
    """Call the OpenAI-compatible chat/completions endpoint and return parsed todo items."""
    api_key = decrypt_api_key(ai_settings.api_key)
    url = f"{ai_settings.base_url.rstrip('/')}/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": ai_settings.model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": note_content},
        ],
        "temperature": 0.3,
        "max_tokens": 2000,
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()

    try:
        data = resp.json()
        raw_text = data["choices"][0]["message"]["content"]
        return _parse_todo_titles(raw_text)
    except (KeyError, IndexError, TypeError) as e:
        logger.error("Unexpected AI API response structure: %s", e)
        raise AIResponseError(f"Unexpected response from AI API: {e}") from e


def _parse_todo_titles(raw_text: str):
    """Extract todo titles from AI response text. Tries JSON parse first, then falls back to line extraction."""
    # Strip markdown code fences if present
    text = raw_text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        if len(lines) > 1:
            lines = lines[1:]  # remove opening fence
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]  # remove closing fence
        text = "\n".join(lines).strip()

    # Try JSON parsing
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return [item["title"] for item in parsed if isinstance(item, dict) and "title" in item]
    except (json.JSONDecodeError, KeyError, TypeError):
        pass

    # Fallback: try to extract JSON array from the text
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if match:
        try:
            parsed = json.loads(match.group(0))
            if isinstance(parsed, list):
                return [
                    item["title"] for item in parsed if isinstance(item, dict) and "title" in item
                ]
        except (json.JSONDecodeError, KeyError, TypeError):
            pass

    return []


# ── Constants ────────────────────────────────────────────────────────────────

MAX_CONTENT_CHARS = 8000


# ── Summarize Action ────────────────────────────────────────────────────────


def summarize_note_todos(note):
    """
    Main entry point: call AI API for a note, create Todo items from the result.
    Returns (todos, count) tuple.
    """
    ai_settings = AISettings.get_solo()

    if not ai_settings.is_configured():
        raise AINotConfiguredError("AI API settings are not configured")

    if not note.content or not note.content.strip():
        raise EmptyContentError("Note content is empty")

    # Truncate content to avoid token limits
    truncated_content = note.content[:MAX_CONTENT_CHARS]

    titles = call_ai_api(ai_settings, truncated_content)

    with transaction.atomic():
        created_todos = []
        for title in titles:
            todo = Todo.objects.create(
                title=title,
                content="",
                category=note.category,
            )
            created_todos.append(todo)

    return created_todos, len(created_todos)


# ── Custom Exceptions ───────────────────────────────────────────────────────


class AIServiceError(Exception):
    """Base exception for AI service errors."""


class AINotConfiguredError(AIServiceError):
    """Raised when AI settings are not configured."""


class EmptyContentError(AIServiceError):
    """Raised when note content is empty."""


class AIResponseError(AIServiceError):
    """Raised when the AI API returns an unexpected response structure."""
