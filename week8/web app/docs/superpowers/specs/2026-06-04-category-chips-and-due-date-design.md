# Design Spec: Category Chips + Due Date Picker

**Date:** 2026-06-04
**Status:** Approved

## Overview

Two feature additions to the note/todo app:

1. **Category chip selector** — Replace free-text category input with a chip/tag bar showing all existing categories, plus a "＋ 新建分类" toggle that expands to a text input for creating new categories on the fly.

2. **Todo due date** — Add a user-defined `due_date` field to todos. Displayed as YYYY-MM-DD in the list. Defaults to today when creating. Uses native `<input type="date">`.

Both features apply to both create and edit flows. Due date is todo-only.

---

## Architecture

### Backend Changes

**Model (`backend/notes/models.py`)**
- Add `due_date = models.DateField(null=True, blank=True, default=date.today)` to `Todo` model.
- Requires `from datetime import date` at top.
- A new migration `0002_*.py` will be auto-generated.
- Note model: no changes.

**Serializer (`backend/notes/serializers.py`)**
- `TodoSerializer.Meta.fields`: `"__all__"` already covers the new field — no change needed (the field is in the model).
- Validation: the DateField handles format validation natively. No custom validator needed.

**No changes needed:** views, urls, admin.

### Frontend Changes

| File | Change |
|------|--------|
| `DetailPanel.vue` | Replace category `<input>` with chip bar + "＋ 新建分类" toggle; add `<input type="date" v-model="editForm.due_date">` (todo only) |
| `TodoItem.vue` | Display `todo.due_date` formatted as YYYY-MM-DD; fallback to `---` if null |
| `MainLayout.vue` | `onCreate()` sets `due_date` default to today for todos |
| `utils/categories.js` | Add `getTodayDateString()` helper |

**No changes needed:** Sidebar (auto-discovers categories), NoteCard/NoteCards, stores/notes.js, API layer, TodoList.

---

## Data Flow

### Category Chips

1. `fetchCategories()` (called on mount) returns all unique categories from backend.
2. `DetailPanel` renders known categories as color-coded chips.
3. Clicking a chip sets `editForm.category = chipLabel`.
4. Clicking "＋ 新建分类" hides the chip and shows a text `<input>` in its place.
5. On Enter/blur, the input value becomes the selected category, and the input collapses back to the chip.
6. On save, the category string is sent via the existing API — no backend changes needed for categories.

### Due Date

1. `MainLayout.vue` `onCreate()` populates `due_date: getTodayDateString()`.
2. `DetailPanel` shows `<input type="date">` only when `store.selectedType === 'todo'`.
3. On save, `due_date` is included in the POST/PUT payload.
4. `TodoItem.vue` displays `todo.due_date` formatted as YYYY-MM-DD.

---

## Component Details

### DetailPanel.vue

**Edit form changes:**

- `editForm` reactive object gains a `due_date` field (`''` by default).
- **Category section** — replace `<input v-model="editForm.category">` with:
  - A wrapping flex container of clickable chips.
  - Chips rendered from a computed `availableCategories` list (presets + `store.categories`).
  - Selected chip gets a highlighted border + background.
  - "无分类" chip (always present) for clearing the selection.
  - "＋ 新建分类" chip as the last item.
  - When clicked, a local `isCreatingCategory` ref becomes `true`, showing an `<input>` instead of the "＋" chip.
  - On Enter or blur: trim value; if non-empty, set `editForm.category = trimmedValue`; set `isCreatingCategory = false`.

- **Due date section** (todos only):
  - `v-if="store.selectedType === 'todo'"`
  - `<input type="date" v-model="editForm.due_date">`
  - Styled consistently with other form inputs.

### TodoItem.vue

- Replace `formatDate(todo.created_at)` with a computed property:
  - If `todo.due_date` exists: format as `YYYY-MM-DD` (split and join or use `formatDate` from categories.js).
  - If `todo.due_date` is null/empty: display `---`.

### MainLayout.vue

- `onCreate()`: when `activeTab === 'todo'`, add `due_date: getTodayDateString()` to the initial object.

### categories.js

- Add:
  ```js
  export function getTodayDateString() {
    const d = new Date()
    return d.toISOString().split('T')[0]
  }
  ```

---

## Edge Cases & Error Handling

| Scenario | Behavior |
|----------|----------|
| Existing todos without `due_date` (pre-migration) | Display `---` in the date column |
| New category input is blank or whitespace-only | Ignore; don't update `editForm.category` |
| Category name > 50 chars | Backend validator returns error; shown via existing toast |
| Due date in the past | Allowed — no validation restriction |
| Due date field on note create/edit form | Hidden via `v-if`; not sent in API payload |
| `due_date` field on note model (backend) | Not added — Note model unchanged |

---

## Testing

**Backend:**
- Add test in `backend/notes/tests.py`: create a todo with `due_date`, assert it's returned correctly.
- Verify migration applies without errors.

**Frontend:**
- No frontend test infrastructure exists; verify manually by running the app.
