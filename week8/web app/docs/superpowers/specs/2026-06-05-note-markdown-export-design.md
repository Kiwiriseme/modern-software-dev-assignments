# Note Markdown Export — Design Spec

**Date:** 2026-06-05
**Scope:** Single-feature — export a note as a `.md` file via the detail panel.

---

## 1. Feature Summary

Add an export button to the note detail panel that downloads the current note as a Markdown (`.md`) file. Implementation is pure frontend using `Blob` + `URL.createObjectURL`.

## 2. UI Placement

In `DetailPanel.vue` header actions bar, between the edit button and the delete button:

```
[←返回] [笔记]          [编辑] [导出] [🗑删除]
```

Constraints:
- Visible only in **read mode** (not while editing).
- Visible only when `store.selectedType === 'note'` (todos are not exportable).
- Uses a download/export-styled SVG icon with tooltip "导出 Markdown".

## 3. Export Logic

New function `exportMarkdown()` in `DetailPanel.vue` `<script setup>`:

1. Read `store.selectedItem.title` and `store.selectedItem.content`.
2. Build Markdown body: `# <title>\n\n<content>`.
3. Sanitize the title to a safe filename:
   - Replace `/ \ : * ? " < > |` with `-`.
   - Trim leading/trailing whitespace.
   - Fallback to `"未命名笔记"` if empty.
   - Append `.md`.
4. Create a `Blob` from the Markdown string (`type: 'text/markdown'`).
5. Create an object URL via `URL.createObjectURL(blob)`.
6. Programmatically click an `<a>` element with `download` attribute.
7. Clean up with `URL.revokeObjectURL(url)` after a short delay.

## 4. Edge Cases

| Case | Behavior |
|------|----------|
| Content is empty | File contains only `# <title>\n\n` — no error. |
| Title contains special characters | Sanitized to safe filename; original title preserved in file body. |
| Detail panel is closed | Button naturally hidden (panel is closed). |
| Very long title | Sanitized filename may be truncated by browser; file body uses full title. |

## 5. Component Boundaries

**Affected unit:** `DetailPanel.vue` only.

**What it does:** Exposes a user action that serializes the currently viewed note to a Markdown file and triggers a browser download.

**Dependencies:**
- `useNotesStore` (already imported) — reads `selectedItem`, `selectedType`.
- Browser APIs: `Blob`, `URL.createObjectURL`, `URL.revokeObjectURL`, `document.createElement('a')`.

**No change:** All other components, backend APIs, store, and routing are untouched.

## 6. Testing

Manual test cases:
1. Export a note with title and content → verify `.md` file downloads with correct `#` + content.
2. Export a note with empty content → verify file is `# 标题` only.
3. Export a note with special characters in title (`/ : * ?`) → verify filename is sanitized.
4. Verify button does NOT appear for todos.
5. Verify button does NOT appear in edit mode.
6. Verify button does NOT appear when no item is selected (panel closed).
