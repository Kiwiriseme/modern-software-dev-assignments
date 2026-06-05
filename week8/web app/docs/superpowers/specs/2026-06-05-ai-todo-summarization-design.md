# AI Todo Summarization Design

## Overview

Add a feature that uses AI to extract and summarize todo items from note content. When viewing a note, a button in the toolbar triggers an AI call (OpenAI-compatible API), which analyzes the note content and creates todo items with the same category as the note. A settings dialog (accessed via a gear icon in the sidebar footer) allows configuring the AI API credentials, stored encrypted in the backend database.

## Feature Summary

| Feature | Description |
|---|---|
| AI Todo Summarization | Extract todo items from note content via AI, add to todo list with note's category (append mode) |
| API Settings | Configure AI API endpoint, model, and key via a modal dialog |
| Privacy | API key encrypted at rest in SQLite, never exposed to frontend |
| Unguided flow | If API is not configured, prompt user to go to settings |

## Architecture

### Backend

#### New Model: `AISettings`

Singleton pattern — only one row in the table.

| Field | Type | Details |
|---|---|---|
| `id` | AutoField | Primary key |
| `api_key` | CharField(512) | AES encrypted, never returned in GET |
| `base_url` | URLField | Default `https://api.openai.com/v1` |
| `model` | CharField(100) | Default `gpt-4o-mini` |
| `updated_at` | DateTimeField | auto_now |

**Encryption:** Django `SECRET_KEY` derives an AES-256 key via SHA-256 hash. The `api_key` field is encrypted on save and decrypted on use. A custom model manager or field handles this transparently.

#### New API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/ai-settings` | Return current settings (api_key masked as `***`, plus `is_configured: bool`) |
| `PUT` | `/api/v1/ai-settings` | Save settings. If `api_key` is `***`, keep existing key unchanged |
| `POST` | `/api/v1/notes/{id}/summarize-todos` | Trigger AI summarization for a note, return created todos |

#### AI Summarization Service

**System prompt (hardcoded in backend):**

```
你是一个任务提取助手。请分析以下笔记内容，提取其中隐含的待办事项。每个待办事项应该是一个具体可执行的任务。以 JSON 数组格式返回，每个元素包含 title 字段。如果没有待办事项，返回空数组 []。

笔记内容：
{note_content}
```

**Flow:**
1. Validate note exists and has non-empty content
2. Check AISettings exists and `is_configured` is true
3. Build OpenAI-compatible request: POST `{base_url}/chat/completions` with `Authorization: Bearer {decrypted_api_key}`, body `{ model, messages: [{role: "system", content: system_prompt}, {role: "user", content: note.content}] }`
4. Parse response: extract JSON array from `choices[0].message.content`
5. For each item in the array, create a Todo with `title`, `category` from the note, `content` empty
6. Return `{ todos: [...], count: N }`

### Frontend

#### New Component: `SettingsDialog.vue`

- Modal dialog with form fields:
  - **API Base URL**: text input, placeholder `https://api.openai.com/v1`
  - **Model**: text input, placeholder `gpt-4o-mini`
  - **API Key**: password input, shows `****` when previously saved
- Save button → PUT `/api/v1/ai-settings`
- Cancel button → close dialog
- Opened by clicking gear icon in Sidebar footer
- On mount, fetches current settings via GET `/api/v1/ai-settings`

#### Modified Component: `Sidebar.vue`

- Add gear icon (⚙) button in the footer area, next to the existing theme toggle button
- Clicking opens `SettingsDialog`

#### Modified Component: `DetailPanel.vue`

- In the toolbar area (near the export Markdown and delete buttons), add a new button:
  - Text: "🤖 AI 总结待办"
  - Visual style: secondary button with blue tint to distinguish from export/delete
  - Only visible when viewing a **note** (not a todo)
- **Click handler:**
  1. Check `is_configured` from cached settings or a quick API check
  2. If **not configured**: Show `ConfirmDialog` with message "请先配置 AI API 设置", buttons: "去设置" (opens SettingsDialog) and "取消"
  3. If **configured**: Button enters loading state ("总结中..." + spinner, disabled), call `POST /api/v1/notes/{id}/summarize-todos`
  4. On success: Toast `已添加 N 个待办事项` (or `未发现待办事项` if count=0), refresh todo list
  5. On error: Toast with error message, button returns to normal state

#### Modified Files: API client (`src/api/index.js`)

- Add: `fetchAISettings()`, `saveAISettings(data)`, `summarizeNoteTodos(noteId)`

#### Modified Files: Pinia store (`src/stores/notes.js`)

- Add state: `aiSettings` (cached settings object), `showSettings` (dialog visibility), `summarizingNoteId` (tracking loading state)
- Add actions: `loadAISettings()`, `saveAISettings(data)`, `summarizeTodos(noteId)`, `openSettings()`, `closeSettings()`

## Data Flow

### Configuration Flow

```
User clicks gear → SettingsDialog opens → GET /api/v1/ai-settings
→ Form populated (key shows ***) → User edits → Save
→ PUT /api/v1/ai-settings → Backend encrypts key → Success
```

### AI Summarization Flow

```
User opens note in DetailPanel → "🤖 AI 总结待办" visible in toolbar
→ Click → Check is_configured
  ├─ false → ConfirmDialog "请先配置" → 去设置 or 取消
  └─ true → Loading state
      → POST /api/v1/notes/{id}/summarize-todos
      → Backend: read note → build prompt → call AI API → parse → create Todos
      → Response: { todos: [...], count: N }
      → Toast + refresh todo list
```

## Error Handling

| Scenario | HTTP Status | Frontend Toast |
|---|---|---|
| Note content empty | 400 | "笔记内容为空" |
| AI settings not configured | 400 | "请先配置 API 设置" |
| AI API timeout (30s) | 504 | "AI 请求超时，请重试" |
| AI API auth error (401) | 502 | "API 密钥无效，请检查设置" |
| AI response malformed (non-JSON) | 500 | "AI 返回格式异常，请重试" |
| Network error | — | Axios interceptor default error message |
| No todos found | 200 | "未发现待办事项" |

## Edge Cases

- **Note content is empty or whitespace-only**: return 400 before calling AI
- **AI returns empty array `[]`**: valid case, return `count: 0`, toast "未发现待办事项"
- **AI returns non-JSON**: parse error, return 500. Attempt basic extraction (look for JSON array in response) as a fallback.
- **Settings deleted between check and summarize**: backend checks at request time, returns 400 if unconfigured
- **Concurrent summarization clicks**: frontend disables button during loading; backend is idempotent (creates new todos each call)
- **Very long note content**: truncate to 8000 chars before sending to AI to avoid token limit issues

## Testing

### Backend Tests (`notes/tests.py`)

| Test | Description |
|---|---|
| `test_get_ai_settings_default` | Unconfigured state returns `is_configured: false` |
| `test_create_ai_settings` | PUT saves settings, API key encrypted at rest |
| `test_get_ai_settings_masks_key` | GET returns `***` not plaintext key |
| `test_update_settings_partial_key` | Passing `***` preserves existing key |
| `test_summarize_no_settings` | POST summarize without configuration → 400 |
| `test_summarize_empty_content` | Note has empty content → 400 |
| `test_summarize_invalid_api_key` | Mock AI API returns 401 → 502 |
| `test_summarize_success` | Mock AI returns valid JSON → todos created with correct category |
| `test_summarize_no_todos` | AI returns `[]` → count=0, no todos created |
| `test_summarize_ai_timeout` | Mock AI times out → 504 |
| `test_summarize_malformed_response` | AI returns non-JSON → 500 |

### Frontend Tests

| Test | Description |
|---|---|
| SettingsDialog renders and opens/closes | Gear click → dialog visible; cancel → dialog hidden |
| SettingsDialog save | Submits correct data, calls API |
| AI button visibility | Shows on note detail, hidden on todo detail |
| Unconfigured flow | Click → confirm dialog → "去设置" opens settings |
| Loading state | Click → button disabled with spinner → recovers after API response |

## Files Changed

| File | Change |
|---|---|
| `backend/notes/models.py` | Add `AISettings` model + encryption manager |
| `backend/notes/serializers.py` | Add `AISettingsSerializer` |
| `backend/notes/views.py` | Add `AISettingsViewSet` + `summarize_todos` action on NoteViewSet |
| `backend/notes/urls.py` | Add routes for ai-settings and summarize-todos |
| `backend/notes/ai_service.py` | **New file:** AI summarization service |
| `frontend/src/api/index.js` | Add 3 new API functions |
| `frontend/src/stores/notes.js` | Add settings and summarization state/actions |
| `frontend/src/components/SettingsDialog.vue` | **New file:** Settings modal |
| `frontend/src/components/Sidebar.vue` | Add gear icon in footer |
| `frontend/src/components/DetailPanel.vue` | Add AI summarize button in toolbar |
