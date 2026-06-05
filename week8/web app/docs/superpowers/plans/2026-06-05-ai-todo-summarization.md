# AI Todo Summarization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an AI-powered feature that summarizes todo items from note content using a user-configured OpenAI-compatible API, with encrypted API key storage and a settings dialog.

**Architecture:** Backend adds an `AISettings` model with Fernet-encrypted API key, a new `ai_service.py` module for calling OpenAI-compatible APIs, a ViewSet for settings CRUD, and a custom action on NoteViewSet for summarization. Frontend adds a `SettingsDialog` component, a gear icon in the Sidebar footer, and an AI summarize button in the DetailPanel toolbar.

**Tech Stack:** Django 4.2, DRF 3.14+, Vue 3 (Composition API + Pinia), marked, DOMPurify, cryptography (Fernet)

---

## File Structure

| File | Change | Responsibility |
|---|---|---|
| `backend/requirements.txt` | Modify | Add `cryptography` dependency |
| `backend/notes/models.py` | Modify | Add `AISettings` model |
| `backend/notes/serializers.py` | Modify | Add `AISettingsSerializer` |
| `backend/notes/ai_service.py` | **Create** | AI API call + response parsing |
| `backend/notes/views.py` | Modify | Add `AISettingsViewSet` + `summarize_todos` action on `NoteViewSet` |
| `backend/notes/urls.py` | Modify | Add routes for ai-settings and summarize-todos |
| `backend/notes/tests.py` | Modify | Add AI settings + summarization tests |
| `frontend/src/api/index.js` | Modify | Add `fetchAISettings`, `saveAISettings`, `summarizeNoteTodos` |
| `frontend/src/stores/notes.js` | Modify | Add settings/summarization state and actions |
| `frontend/src/components/SettingsDialog.vue` | **Create** | Settings modal dialog |
| `frontend/src/components/Sidebar.vue` | Modify | Add gear icon in footer |
| `frontend/src/components/DetailPanel.vue` | Modify | Add AI button in toolbar + unconfigured dialog |
| `frontend/src/views/MainLayout.vue` | Modify | Add SettingsDialog + AI confirm dialog instances |

---

### Task 1: Add cryptography dependency

**Files:**
- Modify: `web app/backend/requirements.txt`

- [ ] **Step 1: Add cryptography to requirements**

```diff
 Django>=4.2,<5.0
 djangorestframework>=3.14,<4.0
 django-cors-headers>=4.0,<5.0
+cryptography>=41.0,<44.0
```

- [ ] **Step 2: Install the dependency**

Run: `cd "web app/backend" && pip install cryptography>=41.0,<44.0`
Expected: package installs without error.

- [ ] **Step 3: Commit**

```bash
git add "web app/backend/requirements.txt"
git commit -m "chore: add cryptography dependency for API key encryption"
```

---

### Task 2: Create AISettings model

**Files:**
- Modify: `web app/backend/notes/models.py`

- [ ] **Step 1: Add AISettings model to models.py**

Append the following code to `web app/backend/notes/models.py`:

```python
class AISettings(models.Model):
    """Singleton model storing AI API configuration. Only one row should exist."""
    api_key = models.CharField(max_length=512, blank=True, default="")
    base_url = models.URLField(default="https://api.openai.com/v1")
    model = models.CharField(max_length=100, default="gpt-4o-mini")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "AI Settings"
        verbose_name_plural = "AI Settings"

    def __str__(self):
        return f"AISettings (model={self.model})"

    def is_configured(self):
        return bool(self.api_key)

    @classmethod
    def get_solo(cls):
        """Return the singleton AISettings instance, creating one if it doesn't exist."""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
```

- [ ] **Step 2: Generate and run the migration**

```bash
cd "web app/backend" && python manage.py makemigrations notes --name "ai_settings"
```

Run: `python manage.py migrate`
Expected: "Applying notes.0003_ai_settings... OK"

- [ ] **Step 3: Verify the model works in Django shell**

Run: `python manage.py shell -c "from notes.models import AISettings; s = AISettings.get_solo(); print(s.model, s.is_configured())"`
Expected: `gpt-4o-mini False`

- [ ] **Step 4: Commit**

```bash
git add "web app/backend/notes/models.py" "web app/backend/notes/migrations/0003_ai_settings.py"
git commit -m "feat: add AISettings singleton model for AI API configuration"
```

---

### Task 3: Create encryption helpers in ai_service.py

**Files:**
- Create: `web app/backend/notes/ai_service.py`

- [ ] **Step 1: Create ai_service.py with encryption functions**

Create `web app/backend/notes/ai_service.py`:

```python
import hashlib
import base64
import json
import logging

import requests
from django.conf import settings
from cryptography.fernet import Fernet, InvalidToken

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
        return ""


# ── AI System Prompt ────────────────────────────────────────────────────────

SYSTEM_PROMPT = (
    "你是一个任务提取助手。请分析以下笔记内容，提取其中隐含的待办事项。"
    "每个待办事项应该是一个具体可执行的任务。"
    "以 JSON 数组格式返回，每个元素包含 title 字段。"
    "如果没有待办事项，返回空数组 []。\n\n"
    "笔记内容：\n{note_content}"
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
            {"role": "system", "content": "你是一个任务提取助手。请分析以下笔记内容，提取其中隐含的待办事项。每个待办事项应该是一个具体可执行的任务。以 JSON 数组格式返回，每个元素包含 title 字段。如果没有待办事项，返回空数组 []。"},
            {"role": "user", "content": note_content},
        ],
        "temperature": 0.3,
        "max_tokens": 2000,
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()

    data = resp.json()
    raw_text = data["choices"][0]["message"]["content"]
    return _parse_todo_titles(raw_text)


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
    import re
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if match:
        try:
            parsed = json.loads(match.group(0))
            if isinstance(parsed, list):
                return [item["title"] for item in parsed if isinstance(item, dict) and "title" in item]
        except (json.JSONDecodeError, KeyError, TypeError):
            pass

    return []


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

    # Truncate content to 8000 chars to avoid token limits
    truncated_content = note.content[:8000]

    titles = call_ai_api(ai_settings, truncated_content)

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
```

- [ ] **Step 2: Commit**

```bash
git add "web app/backend/notes/ai_service.py"
git commit -m "feat: add AI service with encryption helpers and OpenAI-compatible API client"
```

---

### Task 4: Add AISettingsSerializer

**Files:**
- Modify: `web app/backend/notes/serializers.py`

- [ ] **Step 1: Add AISettingsSerializer to serializers.py**

Open `web app/backend/notes/serializers.py` and append:

```python
from notes.models import AISettings


class AISettingsSerializer(serializers.ModelSerializer):
    is_configured = serializers.SerializerMethodField()

    class Meta:
        model = AISettings
        fields = ["api_key", "base_url", "model", "updated_at", "is_configured"]
        read_only_fields = ["updated_at", "is_configured"]

    def get_is_configured(self, obj):
        return obj.is_configured()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Mask the API key in responses
        if instance.api_key:
            data["api_key"] = "***"
        else:
            data["api_key"] = ""
        return data

    def update(self, instance, validated_data):
        api_key = validated_data.get("api_key", "***")
        # If the user sent "***", keep the existing key
        if api_key == "***":
            validated_data.pop("api_key", None)
        else:
            from notes.ai_service import encrypt_api_key
            validated_data["api_key"] = encrypt_api_key(api_key)
        return super().update(instance, validated_data)

    def create(self, validated_data):
        api_key = validated_data.get("api_key", "")
        if api_key and api_key != "***":
            from notes.ai_service import encrypt_api_key
            validated_data["api_key"] = encrypt_api_key(api_key)
        return super().create(validated_data)
```

- [ ] **Step 2: Verify the serializer imports correctly**

Run: `cd "web app/backend" && python -c "from notes.serializers import AISettingsSerializer; print('OK')"`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add "web app/backend/notes/serializers.py"
git commit -m "feat: add AISettingsSerializer with API key masking and encryption"
```

---

### Task 5: Add AISettingsViewSet and summarize_todos action

**Files:**
- Modify: `web app/backend/notes/views.py`

- [ ] **Step 1: Add AISettingsViewSet and modify NoteViewSet in views.py**

Replace the content of `web app/backend/notes/views.py`:

```python
from django.db import models
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from notes.models import Note, Todo, AISettings
from notes.serializers import NoteSerializer, TodoSerializer, AISettingsSerializer
from notes.ai_service import (
    summarize_note_todos,
    AINotConfiguredError,
    EmptyContentError,
    AIServiceError,
)


class BaseItemViewSet(viewsets.ModelViewSet):
    """共享过滤逻辑的基类"""

    def filter_queryset_by_params(self, queryset):
        category = self.request.query_params.get("category", None)
        q = self.request.query_params.get("q", None)
        if category and category != "全部":
            queryset = queryset.filter(category=category)
        if q:
            queryset = queryset.filter(
                models.Q(title__icontains=q) | models.Q(content__icontains=q)
            )
        return queryset


class TodoViewSet(BaseItemViewSet):
    serializer_class = TodoSerializer

    def get_queryset(self):
        return self.filter_queryset_by_params(Todo.objects.all())


class NoteViewSet(BaseItemViewSet):
    serializer_class = NoteSerializer

    def get_queryset(self):
        return self.filter_queryset_by_params(Note.objects.all())

    @action(detail=True, methods=["post"], url_path="summarize-todos")
    def summarize_todos(self, request, pk=None):
        """Call AI to extract todo items from the note content."""
        note = self.get_object()
        try:
            todos, count = summarize_note_todos(note)
        except AINotConfiguredError:
            return Response(
                {"detail": "请先配置 API 设置"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except EmptyContentError:
            return Response(
                {"detail": "笔记内容为空"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except AIServiceError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            # Handle requests.exceptions.RequestException (network, timeout, auth errors)
            error_str = str(e)
            if "401" in error_str or "Unauthorized" in error_str or "403" in error_str:
                return Response(
                    {"detail": "API 密钥无效，请检查设置"},
                    status=status.HTTP_502_BAD_GATEWAY,
                )
            if "timeout" in error_str.lower() or "Timeout" in error_str:
                return Response(
                    {"detail": "AI 请求超时，请重试"},
                    status=status.HTTP_504_GATEWAY_TIMEOUT,
                )
            return Response(
                {"detail": f"AI API 请求失败: {error_str}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        serializer = TodoSerializer(todos, many=True)
        return Response({"todos": serializer.data, "count": count})


class AISettingsViewSet(viewsets.ModelViewSet):
    """CRUD for AI settings. Only supports get/update since it's a singleton."""
    serializer_class = AISettingsSerializer
    http_method_names = ["get", "put", "head", "options"]

    def get_queryset(self):
        # Return the singleton
        return AISettings.objects.filter(pk=AISettings.get_solo().pk)

    def get_object(self):
        return AISettings.get_solo()
```

- [ ] **Step 2: Verify imports**

Run: `cd "web app/backend" && python -c "from notes.views import NoteViewSet, AISettingsViewSet; print('OK')"`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add "web app/backend/notes/views.py"
git commit -m "feat: add AISettingsViewSet and summarize_todos action on NoteViewSet"
```

---

### Task 6: Add URL routes for AI settings and summarization

**Files:**
- Modify: `web app/backend/notes/urls.py`

- [ ] **Step 1: Add new routes to urls.py**

Replace the content of `web app/backend/notes/urls.py`:

```python
from django.db import transaction
from django.urls import path
from rest_framework import status
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter
from rest_framework.views import APIView

from notes.models import Note, Todo
from notes.views import NoteViewSet, TodoViewSet, AISettingsViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r"todos", TodoViewSet, basename="todo")
router.register(r"notes", NoteViewSet, basename="note")
router.register(r"ai-settings", AISettingsViewSet, basename="ai-settings")


class CategoryListView(APIView):
    def get(self, request):
        todo_categories = (
            Todo.objects.exclude(category="").values_list("category", flat=True).distinct()
        )
        note_categories = (
            Note.objects.exclude(category="").values_list("category", flat=True).distinct()
        )
        all_categories = sorted(set(list(todo_categories) + list(note_categories)))
        return Response(all_categories)


class CategoryDeleteView(APIView):
    @transaction.atomic
    def delete(self, request):
        name = request.query_params.get("name", "")
        if not name:
            return Response({"detail": "缺少分类名称参数"}, status=status.HTTP_400_BAD_REQUEST)
        todo_count = Todo.objects.filter(category=name).update(category="")
        note_count = Note.objects.filter(category=name).update(category="")
        total = todo_count + note_count
        return Response({"deleted": name, "cleared": total})


urlpatterns = router.urls + [
    path("categories", CategoryListView.as_view(), name="categories"),
    path("categories/delete", CategoryDeleteView.as_view(), name="category-delete"),
]
```

- [ ] **Step 2: Verify routes are registered**

Run: `cd "web app/backend" && python manage.py show_urls 2>/dev/null || python -c "from notes.urls import urlpatterns; print([p.name for p in urlpatterns])"`
Expected: Should include `ai-settings-list` and `ai-settings-detail` in the output.

- [ ] **Step 3: Commit**

```bash
git add "web app/backend/notes/urls.py"
git commit -m "feat: add AI settings and summarize-todos URL routes"
```

---

### Task 7: Add backend tests

**Files:**
- Modify: `web app/backend/notes/tests.py`

- [ ] **Step 1: Add test classes to tests.py**

Append the following test classes to `web app/backend/notes/tests.py`:

```python
from unittest.mock import patch, MagicMock

from notes.models import AISettings
from notes.ai_service import encrypt_api_key, decrypt_api_key


class AISettingsModelTest(TestCase):
    def test_get_solo_creates_default(self):
        self.assertEqual(AISettings.objects.count(), 0)
        s = AISettings.get_solo()
        self.assertEqual(s.model, "gpt-4o-mini")
        self.assertEqual(s.base_url, "https://api.openai.com/v1")
        self.assertEqual(s.api_key, "")
        self.assertFalse(s.is_configured())

    def test_get_solo_returns_existing(self):
        s1 = AISettings.get_solo()
        s2 = AISettings.get_solo()
        self.assertEqual(s1.pk, s2.pk)
        self.assertEqual(AISettings.objects.count(), 1)

    def test_is_configured_with_key(self):
        s = AISettings.get_solo()
        s.api_key = encrypt_api_key("sk-test-key")
        s.save()
        self.assertTrue(s.is_configured())


class AISettingsEncryptionTest(TestCase):
    def test_encrypt_decrypt_roundtrip(self):
        plaintext = "sk-test-api-key-12345"
        ciphertext = encrypt_api_key(plaintext)
        self.assertNotEqual(ciphertext, plaintext)
        self.assertNotIn("sk-test", ciphertext)
        decrypted = decrypt_api_key(ciphertext)
        self.assertEqual(decrypted, plaintext)

    def test_encrypt_empty_key(self):
        self.assertEqual(encrypt_api_key(""), "")

    def test_decrypt_empty_key(self):
        self.assertEqual(decrypt_api_key(""), "")


class AISettingsAPITest(APITestCase):
    def test_get_unconfigured_settings(self):
        response = self.client.get("/api/v1/ai-settings/1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_configured"])
        self.assertEqual(response.data["api_key"], "")
        self.assertEqual(response.data["model"], "gpt-4o-mini")

    def test_put_settings_masks_key_in_response(self):
        response = self.client.put(
            "/api/v1/ai-settings/1",
            {
                "api_key": "sk-my-secret-key",
                "base_url": "https://api.openai.com/v1",
                "model": "gpt-4o",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["api_key"], "***")

    def test_put_settings_encrypts_key_at_rest(self):
        self.client.put(
            "/api/v1/ai-settings/1",
            {"api_key": "sk-my-secret-key", "base_url": "https://api.openai.com/v1", "model": "gpt-4o"},
            format="json",
        )
        s = AISettings.get_solo()
        # The stored value should be encrypted, not the plaintext
        self.assertNotEqual(s.api_key, "sk-my-secret-key")
        self.assertTrue(len(s.api_key) > 0)
        # But it should decrypt back
        self.assertEqual(decrypt_api_key(s.api_key), "sk-my-secret-key")

    def test_put_star_preserves_existing_key(self):
        # First set a key
        self.client.put(
            "/api/v1/ai-settings/1",
            {"api_key": "sk-original-key", "base_url": "https://api.openai.com/v1", "model": "gpt-4o"},
            format="json",
        )
        # Then update with *** to preserve
        self.client.put(
            "/api/v1/ai-settings/1",
            {"api_key": "***", "base_url": "https://api.deepseek.com/v1", "model": "deepseek-chat"},
            format="json",
        )
        s = AISettings.get_solo()
        self.assertEqual(decrypt_api_key(s.api_key), "sk-original-key")
        self.assertEqual(s.model, "deepseek-chat")
        self.assertEqual(s.base_url, "https://api.deepseek.com/v1")


class AISummarizeAPITest(APITestCase):
    def setUp(self):
        self.note = Note.objects.create(
            title="Meeting Notes",
            content="需要完成项目报告\n需要回复客户邮件\n预约下周的会议室",
            category="工作",
        )

    def test_summarize_without_settings(self):
        response = self.client.post(f"/api/v1/notes/{self.note.id}/summarize-todos")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("请先配置", response.data["detail"])

    def test_summarize_empty_content(self):
        AISettings.get_solo()  # ensure exists
        note = Note.objects.create(title="Empty", content="", category="工作")
        # Configure AI settings
        s = AISettings.get_solo()
        s.api_key = encrypt_api_key("sk-test")
        s.save()
        response = self.client.post(f"/api/v1/notes/{note.id}/summarize-todos")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("为空", response.data["detail"])

    @patch("notes.ai_service.requests.post")
    def test_summarize_success(self, mock_post):
        # Configure AI settings
        s = AISettings.get_solo()
        s.api_key = encrypt_api_key("sk-test")
        s.save()

        # Mock AI response
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": '[{"title":"完成项目报告"},{"title":"回复客户邮件"},{"title":"预约会议室"}]'}}]
        }
        mock_post.return_value = mock_resp

        response = self.client.post(f"/api/v1/notes/{self.note.id}/summarize-todos")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)
        self.assertEqual(len(response.data["todos"]), 3)

        # Verify todos were created with correct category
        todos = Todo.objects.filter(category="工作")
        self.assertEqual(todos.count(), 3)
        titles = [t.title for t in todos]
        self.assertIn("完成项目报告", titles)
        self.assertIn("回复客户邮件", titles)
        self.assertIn("预约会议室", titles)

    @patch("notes.ai_service.requests.post")
    def test_summarize_no_todos_found(self, mock_post):
        s = AISettings.get_solo()
        s.api_key = encrypt_api_key("sk-test")
        s.save()

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": "[]"}}]
        }
        mock_post.return_value = mock_resp

        response = self.client.post(f"/api/v1/notes/{self.note.id}/summarize-todos")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)
        self.assertEqual(len(response.data["todos"]), 0)

    @patch("notes.ai_service.requests.post")
    def test_summarize_ai_returns_401(self, mock_post):
        s = AISettings.get_solo()
        s.api_key = encrypt_api_key("sk-test")
        s.save()

        mock_resp = MagicMock()
        mock_resp.status_code = 401
        mock_resp.json.return_value = {"error": "Unauthorized"}
        mock_resp.raise_for_status.side_effect = Exception("401 Client Error: Unauthorized")
        mock_post.return_value = mock_resp

        response = self.client.post(f"/api/v1/notes/{self.note.id}/summarize-todos")
        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertIn("密钥无效", response.data["detail"])

    @patch("notes.ai_service.requests.post")
    def test_summarize_ai_timeout(self, mock_post):
        s = AISettings.get_solo()
        s.api_key = encrypt_api_key("sk-test")
        s.save()

        import requests as requests_lib
        mock_post.side_effect = requests_lib.exceptions.Timeout("Connection timed out")

        response = self.client.post(f"/api/v1/notes/{self.note.id}/summarize-todos")
        self.assertEqual(response.status_code, status.HTTP_504_GATEWAY_TIMEOUT)

    @patch("notes.ai_service.requests.post")
    def test_summarize_malformed_response(self, mock_post):
        s = AISettings.get_solo()
        s.api_key = encrypt_api_key("sk-test")
        s.save()

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": "这是一些随意的文本，没有JSON"}}]
        }
        mock_post.return_value = mock_resp

        response = self.client.post(f"/api/v1/notes/{self.note.id}/summarize-todos")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)

    @patch("notes.ai_service.requests.post")
    def test_summarize_with_code_fence_json(self, mock_post):
        s = AISettings.get_solo()
        s.api_key = encrypt_api_key("sk-test")
        s.save()

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": '```json\n[{"title":"任务A"},{"title":"任务B"}]\n```'}}]
        }
        mock_post.return_value = mock_resp

        response = self.client.post(f"/api/v1/notes/{self.note.id}/summarize-todos")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
```

- [ ] **Step 2: Run the tests**

```bash
cd "web app/backend" && python manage.py test notes.tests.AISettingsModelTest notes.tests.AISettingsEncryptionTest notes.tests.AISettingsAPITest notes.tests.AISummarizeAPITest -v 2
```
Expected: all 20+ tests pass.

- [ ] **Step 3: Commit**

```bash
git add "web app/backend/notes/tests.py"
git commit -m "test: add AI settings and summarization backend tests (20 tests)"
```

---

### Task 8: Add frontend API functions

**Files:**
- Modify: `web app/frontend/src/api/index.js`

- [ ] **Step 1: Add three new API functions**

Open `web app/frontend/src/api/index.js` and append before `export default api`:

```js
export function fetchAISettings() {
  return api.get('/ai-settings/1')
}

export function saveAISettings(data) {
  return api.put('/ai-settings/1', data)
}

export function summarizeNoteTodos(noteId) {
  return api.post(`/notes/${noteId}/summarize-todos`)
}
```

- [ ] **Step 2: Verify the file still parses**

Run: `cd "web app/frontend" && node -e "require('./src/api/index.js')" 2>/dev/null || echo "ESM file — verify via build"`
(For ESM files, verification comes during the Vite build in a later step.)

- [ ] **Step 3: Commit**

```bash
git add "web app/frontend/src/api/index.js"
git commit -m "feat: add frontend API functions for AI settings and summarization"
```

---

### Task 9: Add store state and actions for AI

**Files:**
- Modify: `web app/frontend/src/stores/notes.js`

- [ ] **Step 1: Add imports at the top**

In `web app/frontend/src/stores/notes.js`, update the import block:

```js
import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  fetchTodos,
  fetchNotes,
  fetchCategories,
  createTodo,
  createNote,
  fetchTodo,
  fetchNote,
  updateTodo,
  updateNote,
  patchTodo,
  deleteTodo,
  deleteNote,
  deleteCategory,
  fetchAISettings,
  saveAISettings,
  summarizeNoteTodos,
} from '../api/index.js'
```

- [ ] **Step 2: Add new state variables**

Add the following after the existing state declarations (after `const pendingLeave = ref(null)`):

```js
  // AI settings state
  const aiSettings = ref(null)
  const showSettings = ref(false)
  const summarizingNoteId = ref(null)
  const showAIConfigurePrompt = ref(false)
  const pendingAIConfigureResolve = ref(null)
```

- [ ] **Step 3: Add new actions**

Add the following functions before the `return` statement:

```js
  async function loadAISettings() {
    try {
      const res = await fetchAISettings()
      aiSettings.value = res.data
    } catch (e) {
      console.error('Failed to load AI settings', e)
    }
  }

  async function saveAISettingsData(data) {
    const res = await saveAISettings(data)
    aiSettings.value = res.data
    showSettings.value = false
    return res.data
  }

  function openSettings() {
    showSettings.value = true
    loadAISettings()
  }

  function closeSettings() {
    showSettings.value = false
  }

  async function summarizeTodos(noteId) {
    if (!aiSettings.value?.is_configured) {
      // Prompt user to configure first
      return new Promise((resolve) => {
        pendingAIConfigureResolve.value = resolve
        showAIConfigurePrompt.value = true
      })
    }
    try {
      summarizingNoteId.value = noteId
      const res = await summarizeNoteTodos(noteId)
      return { success: true, count: res.data.count, todos: res.data.todos }
    } catch (e) {
      const detail = e.response?.data?.detail || e.message || 'AI 总结失败'
      return { success: false, error: detail }
    } finally {
      summarizingNoteId.value = null
    }
  }

  function resolveAIConfigure(action) {
    showAIConfigurePrompt.value = false
    if (pendingAIConfigureResolve.value) {
      pendingAIConfigureResolve.value({ action })
      pendingAIConfigureResolve.value = null
    }
  }
```

- [ ] **Step 4: Add new exports in the return statement**

Add to the return object:

```js
      aiSettings, showSettings, summarizingNoteId,
      showAIConfigurePrompt,
      loadAISettings, saveAISettingsData,
      openSettings, closeSettings,
      summarizeTodos, resolveAIConfigure,
```

- [ ] **Step 5: Commit**

```bash
git add "web app/frontend/src/stores/notes.js"
git commit -m "feat: add AI settings and summarization state to Pinia store"
```

---

### Task 10: Create SettingsDialog component

**Files:**
- Create: `web app/frontend/src/components/SettingsDialog.vue`

- [ ] **Step 1: Create SettingsDialog.vue**

Create `web app/frontend/src/components/SettingsDialog.vue`:

```vue
<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="store.showSettings" class="overlay" @click.self="store.closeSettings()">
        <div class="dialog">
          <div class="dialog-header">
            <h2 class="dialog-title">⚙ API 设置</h2>
            <p class="dialog-subtitle">配置 AI 服务以使用待办事项总结功能</p>
          </div>

          <form class="dialog-body" @submit.prevent="save">
            <div class="form-group">
              <label class="form-label">API Base URL</label>
              <input
                v-model="form.base_url"
                type="url"
                class="form-input"
                placeholder="https://api.openai.com/v1"
              />
            </div>

            <div class="form-group">
              <label class="form-label">Model</label>
              <input
                v-model="form.model"
                type="text"
                class="form-input"
                placeholder="gpt-4o-mini"
              />
            </div>

            <div class="form-group">
              <label class="form-label">API Key</label>
              <input
                v-model="form.api_key"
                type="password"
                class="form-input"
                placeholder="sk-..."
                autocomplete="off"
              />
              <p class="form-hint">密钥将加密存储在本地数据库中，不会上传到任何第三方服务</p>
            </div>

            <div class="dialog-actions">
              <button type="button" class="btn-cancel" @click="store.closeSettings()">取消</button>
              <button type="submit" class="btn-save">保存</button>
            </div>
          </form>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useNotesStore } from '../stores/notes.js'

const store = useNotesStore()
const form = ref({ base_url: '', model: '', api_key: '' })

watch(() => store.aiSettings, (settings) => {
  if (settings) {
    form.value = {
      base_url: settings.base_url || '',
      model: settings.model || '',
      api_key: settings.api_key || '',
    }
  }
})

async function save() {
  const data = {
    base_url: form.value.base_url || 'https://api.openai.com/v1',
    model: form.value.model || 'gpt-4o-mini',
    api_key: form.value.api_key || '***',
  }
  store.saveAISettingsData(data)
}
</script>

<style scoped>
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(45, 36, 24, 0.35);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10001;
}

.dialog {
  background: var(--bg-surface);
  border-radius: var(--radius-lg);
  min-width: 420px;
  max-width: 480px;
  box-shadow: var(--shadow-xl);
  border: 1px solid var(--border-light);
}

.dialog-header {
  padding: var(--space-xl) var(--space-xl) 0;
}

.dialog-title {
  font-family: var(--font-display);
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 var(--space-xs) 0;
}

.dialog-subtitle {
  font-size: 0.8125rem;
  color: var(--text-muted);
  margin: 0 0 var(--space-md) 0;
}

.dialog-body {
  padding: var(--space-lg) var(--space-xl) var(--space-xl);
}

.form-group {
  margin-bottom: var(--space-lg);
}

.form-label {
  display: block;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: var(--space-xs);
  letter-spacing: 0.03em;
  text-transform: uppercase;
}

.form-input {
  width: 100%;
  padding: 9px var(--space-md);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  font-size: 0.875rem;
  color: var(--text-primary);
  background: var(--bg-page);
  outline: none;
  transition: all var(--duration-fast) var(--ease-out);
  box-sizing: border-box;
  font-family: var(--font-mono);
}

.form-input:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-soft);
  background: var(--bg-surface);
}

.form-hint {
  font-size: 0.6875rem;
  color: var(--text-muted);
  margin: var(--space-xs) 0 0 0;
}

.dialog-actions {
  display: flex;
  gap: var(--space-md);
  justify-content: flex-end;
  padding-top: var(--space-sm);
}

.btn-cancel {
  padding: 9px var(--space-xl);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--bg-surface);
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 0.8125rem;
  font-weight: 500;
  transition: all var(--duration-fast) var(--ease-out);
}

.btn-cancel:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.btn-save {
  padding: 9px var(--space-xl);
  border: none;
  border-radius: var(--radius-sm);
  background: var(--accent);
  color: var(--text-inverse);
  cursor: pointer;
  font-size: 0.8125rem;
  font-weight: 500;
  box-shadow: var(--shadow-sm);
  transition: all var(--duration-fast) var(--ease-out);
}

.btn-save:hover {
  background: var(--accent-hover);
  box-shadow: var(--shadow-md);
}

/* Transition */
.modal-enter-active {
  transition: all 0.25s var(--ease-out);
}
.modal-leave-active {
  transition: all 0.15s ease-in;
}
.modal-enter-from {
  opacity: 0;
}
.modal-enter-from .dialog {
  transform: scale(0.95) translateY(8px);
}
.modal-leave-to {
  opacity: 0;
}
</style>
```

- [ ] **Step 2: Verify the file is syntactically valid**

Run: `cd "web app/frontend" && npx vue-tsc --noEmit --pretty 2>&1 | head -20 || echo "SFC — verified by build later"`

- [ ] **Step 3: Commit**

```bash
git add "web app/frontend/src/components/SettingsDialog.vue"
git commit -m "feat: add SettingsDialog component for AI API configuration"
```

---

### Task 11: Add gear icon to Sidebar footer

**Files:**
- Modify: `web app/frontend/src/components/Sidebar.vue`

- [ ] **Step 1: Add the gear button in the sidebar-footer**

In `web app/frontend/src/components/Sidebar.vue`, add the gear button between the `footer-divider` and `ThemeToggle`:

Change this section of the template:
```html
      <div class="footer-divider"></div>
      <ThemeToggle />
```

To:
```html
      <div class="footer-divider"></div>
      <div class="footer-actions">
        <ThemeToggle />
        <span class="action-divider"></span>
        <button
          class="settings-btn"
          @click="store.openSettings()"
          aria-label="API 设置"
          title="API 设置"
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <circle cx="8" cy="8" r="2.5" stroke="currentColor" stroke-width="1.2"/>
            <path d="M8 1.5v1.5M8 13v1.5M1.5 8H3M13 8h1.5M3.4 3.4l1.06 1.06M11.54 11.54l1.06 1.06M3.4 12.6l1.06-1.06M11.54 4.46l1.06-1.06" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
          </svg>
        </button>
      </div>
```

- [ ] **Step 2: Update the script import**

Update the import line:
```js
import { useNotesStore } from '../stores/notes.js'
```
(Already present — verify it's there.)

- [ ] **Step 3: Add styles for the new elements**

Append before the closing `</style>` tag:

```css
.footer-actions {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-xs);
}

.action-divider {
  width: 1px;
  height: 16px;
  background: var(--border-light);
}

.settings-btn {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  transition: all var(--duration-fast) var(--ease-out);
  border: none;
  background: transparent;
  cursor: pointer;
  padding: 0;
}

.settings-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}
```

- [ ] **Step 4: Commit**

```bash
git add "web app/frontend/src/components/Sidebar.vue"
git commit -m "feat: add gear icon for API settings in Sidebar footer"
```

---

### Task 12: Add AI summarize button to DetailPanel

**Files:**
- Modify: `web app/frontend/src/components/DetailPanel.vue`

- [ ] **Step 1: Add the AI summarize button in the toolbar**

In the `header-actions` div, add the AI button between the export button and the delete button:

Change:
```html
          <button
            v-if="!isEditing && store.selectedType === 'note'"
            class="action-btn icon-only"
            @click="exportMarkdown"
            aria-label="导出 Markdown"
            title="导出 Markdown"
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M8 2v8M5 7l3 3 3-3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M3 11v1.5a1 1 0 001 1h8a1 1 0 001-1V11" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
          </button>
          <button
```

To:
```html
          <button
            v-if="!isEditing && store.selectedType === 'note'"
            class="action-btn icon-only"
            @click="exportMarkdown"
            aria-label="导出 Markdown"
            title="导出 Markdown"
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M8 2v8M5 7l3 3 3-3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M3 11v1.5a1 1 0 001 1h8a1 1 0 001-1V11" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
          </button>
          <button
            v-if="!isEditing && store.selectedType === 'note'"
            class="action-btn icon-only ai-btn"
            :class="{ loading: store.summarizingNoteId === store.selectedItem?.id }"
            :disabled="store.summarizingNoteId === store.selectedItem?.id"
            @click="onAISummarize"
            aria-label="AI 总结待办事项"
            title="AI 总结待办事项"
          >
            <svg v-if="store.summarizingNoteId !== store.selectedItem?.id" width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M5 7l3-4 3 4M5 9l3 4 3-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              <circle cx="8" cy="5" r="1" fill="currentColor" opacity="0.3"/>
              <circle cx="8" cy="11" r="1" fill="currentColor" opacity="0.3"/>
            </svg>
            <div v-else class="mini-spinner"></div>
          </button>
          <button
```

- [ ] **Step 2: Add the summarization handler**

Add this function in the `<script setup>` block, after `function exportMarkdown()`:

```js
async function onAISummarize() {
  const note = store.selectedItem
  if (!note) return

  const result = await store.summarizeTodos(note.id)
  if (result === undefined) {
    // User was prompted to configure API (showAIConfigurePrompt is now true)
    return
  }
  if (result.success) {
    emit('toast', {
      message: result.count > 0 ? `已添加 ${result.count} 个待办事项` : '未发现待办事项',
      type: 'success',
    })
    // Refresh todos if we're on the todo tab or need updated counts
    if (store.activeTab === 'todo') {
      try { await store.loadTodos() } catch (e) { /* ignore */ }
    }
    // Also reload categories in case new ones were created (not needed here, but refresh counts)
    try { await store.loadCategories() } catch (e) { /* ignore */ }
  } else {
    emit('toast', { message: result.error || 'AI 总结失败', type: 'error' })
  }
}
```

- [ ] **Step 3: Add styles for the AI button and spinner**

Append before the closing `</style>` tag:

```css
.action-btn.icon-only.ai-btn {
  color: var(--accent);
}

.action-btn.icon-only.ai-btn:hover:not(:disabled) {
  background: var(--accent-soft);
  color: var(--accent-hover);
}

.action-btn.icon-only.ai-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.action-btn.icon-only.ai-btn.loading {
  background: var(--accent-soft);
}

.mini-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid var(--border);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
```

- [ ] **Step 4: Commit**

```bash
git add "web app/frontend/src/components/DetailPanel.vue"
git commit -m "feat: add AI summarize button to DetailPanel toolbar"
```

---

### Task 13: Integrate SettingsDialog and AI configure prompt in MainLayout

**Files:**
- Modify: `web app/frontend/src/views/MainLayout.vue`

- [ ] **Step 1: Add SettingsDialog and AI configure ConfirmDialog to the template**

Add after the leave-confirm `ConfirmDialog` in the template:

```html
    <SettingsDialog />
    <ConfirmDialog
      :visible="store.showAIConfigurePrompt"
      message="请先配置 AI API 设置"
      confirm-text="去设置"
      cancel-text="取消"
      @confirm="onAIConfigureGoSettings"
      @cancel="store.resolveAIConfigure('cancel')"
    />
```

- [ ] **Step 2: Add the import**

```js
import SettingsDialog from '../components/SettingsDialog.vue'
```

- [ ] **Step 3: Add the handler function**

Add after `onRequestDeleteCategory`:

```js
function onAIConfigureGoSettings() {
  store.resolveAIConfigure('go-settings')
  store.openSettings()
}
```

- [ ] **Step 4: Load AI settings on mount**

In the `onMounted` block, add `store.loadAISettings()` to the promises:

```js
onMounted(async () => {
  try {
    await Promise.all([
      store.loadTodos(),
      store.loadNotes(),
      store.loadCategories(),
      store.loadAISettings(),
    ])
  } catch (e) {
    showToast({ message: '加载失败', type: 'error' })
  }
})
```

- [ ] **Step 5: Run the Vite build to check for errors**

```bash
cd "web app/frontend" && npx vite build 2>&1 | tail -15
```
Expected: Build succeeds without errors.

- [ ] **Step 6: Commit**

```bash
git add "web app/frontend/src/views/MainLayout.vue"
git commit -m "feat: integrate SettingsDialog and AI configure prompt in MainLayout"
```

---

### Task 14: End-to-end verification

**Files:** (none — verification only)

- [ ] **Step 1: Run all backend tests**

```bash
cd "web app/backend" && python manage.py test notes -v 2
```
Expected: all tests pass (previous tests + new AI tests, ~40+ total).

- [ ] **Step 2: Run the frontend dev server and verify**

```bash
cd "web app/frontend" && npx vite build --mode production 2>&1 | tail -10
```
Expected: Build succeeds.

- [ ] **Step 3: Start backend and frontend, manual smoke test**

Start the backend:
```bash
cd "web app/backend" && python manage.py runserver 8000 &
```

Start the frontend:
```bash
cd "web app/frontend" && npx vite --port 5173 &
```

Manual test steps:
1. Open http://localhost:5173
2. Observe gear icon (⚙) in Sidebar footer
3. Click gear → Settings Dialog opens
4. Enter API settings → Save → dialog closes
5. Create a note with content containing todo-like items
6. Open the note in DetailPanel
7. Observe "AI 总结待办" button in toolbar (between export and delete)
8. Click → Loading spinner → Toast notification → Todos appear in list
9. Repeat without configuring API → ConfirmDialog shows "请先配置" → "去设置" opens settings

- [ ] **Step 4: Commit any final adjustments**

```bash
git add -A "web app/"
git commit -m "chore: final integration verification"
```
