# Category Management Improvements — Design Spec

**Date:** 2026-06-04
**Status:** Design (awaiting user review)

## Problem Summary

1. **Category creation is not real-time:** When a user creates a new category via the category chip bar in the detail panel, it only sets the local edit form field — the sidebar's category list does not update until a todo/note is saved and the categories API is reloaded.
2. **No category deletion:** Categories can only be added, never removed.

## Design

### Part 1: Real-Time Category Creation + Save Button

**Root cause:** `DetailPanel.vue`'s `confirmNewCategory()` only sets `editForm.category` — it never updates `store.categories`, so `Sidebar.vue`'s `displayCategories` computed property remains stale.

**Changes:**

| Layer | File | Change |
|-------|------|--------|
| Store | `stores/notes.js` | Add `addCategory(name)` action: pushes the name into `categories.value` if not already present. |
| Utility | `utils/categories.js` | Add `generateCategoryColor(name)` and `generateCategoryBgColor(name)` — produces deterministic text/background colors from a hash of the category name string, so custom categories get a consistent and unique color-coded chip appearance. Same name always yields the same color across refreshes. |
| Component | `components/DetailPanel.vue` | Add a save/confirm button (checkmark icon) next to the new-category input. On confirm (Enter or button click), call `store.addCategory(trimmedName)` then set `editForm.category` to the new name so it becomes the actively selected category. |

**Flow:**
User types category name → clicks save button (or presses Enter) → category pushed to `store.categories` → sidebar reactively displays it → `editForm.category` set to the new name → the new category chip is immediately shown as selected in the chip bar.

**Auto-select behavior:** After confirming a new category, `editForm.category` is set to the new name, so the category chip for the newly created category appears selected. This provides immediate visual feedback that the category was created and is now applied to the current item being edited.

**Color allocation for custom categories:** `generateCategoryColor(name)` hashes the category name string to produce a deterministic HSL color value. A corresponding `generateCategoryBgColor(name)` produces a lighter background variant of the same hue. Since the hash is based on the category name, identical names always yield identical colors — even across page refreshes and different sessions.

**`store.categories` data source:** On app mount (`MainLayout.vue` `onMounted`), `store.loadCategories()` calls `GET /api/v1/categories`. The backend query (`CategoryListView`) collects distinct category values from both the `Todo` and `Note` tables via `.values_list("category", flat=True).distinct()`, returning a merged/sorted array of all category names currently in use. This means a category only appears in the sidebar if at least one todo or note has that category value assigned.

---

### Part 2: Category Deletion

**Backend:**

| Layer | File | Change |
|-------|------|--------|
| Endpoint | `notes/urls.py` | Add `DELETE /api/v1/categories` route. Query param `?name=<category>`. |
| View | `notes/views.py` | Add `CategoryDeleteView(APIView)` — finds all `Todo` and `Note` records with `category == name`, clears their category field to `""`, saves them, returns `{"deleted": "<name>", "cleared": <count>}`. |

**Frontend:**

| Layer | File | Change |
|-------|------|--------|
| API | `api/index.js` | Add `deleteCategory(name)` function: `DELETE /api/v1/categories?name=<name>`. |
| Store | `stores/notes.js` | Add `removeCategory(name)` action: calls the API, removes the category from `categories.value`, adds it to `deletedCategories` ref (session-memory to hide preset categories until refresh). Also resets `activeCategory` to `'全部'` if the deleted category was the active filter. |
| Component | `components/Sidebar.vue` | Add a delete button (`×`) on each category item, visible on hover. Emits `delete-category` with the category name. Update `displayCategories` to filter out names in `store.deletedCategories`. |
| View | `views/MainLayout.vue` | Handle the `delete-category` event from Sidebar: set `confirmMessage` and `pendingDeleteCategory`, show `ConfirmDialog`. On confirm, call `store.removeCategory(name)`. On success, show toast. |

**Edge cases handled:**

- **"全部" (All):** No delete button rendered.
- **Active filter is deleted:** `activeCategory` resets to `'全部'` automatically in `removeCategory()`.
- **Session persistence:** `deletedCategories` is in-memory only. A page refresh re-derives categories from the backend (which now has no items with the deleted category), so custom categories naturally disappear; preset categories re-appear but can be deleted again.
- **Confirmation dialog:** Reuses existing `ConfirmDialog` with message: "确定要删除分类「{name}」吗？所有属于该分类的条目将变为无分类状态。"
- **Toast feedback:** Success toast on delete, error toast on API failure.

---

## Data Flow (Delete)

```
Sidebar × button click
  → emit('delete-category', catName)
  → MainLayout sets confirmMessage + pendingDeleteCategory
  → ConfirmDialog shown
  → User confirms
  → store.removeCategory(catName)
    → DELETE /api/v1/categories?name=catName
    → Backend clears category field on all matching Todo/Note rows
    → categories.value.splice(idx, 1)
    → deletedCategories.value.push(catName)
    → if activeCategory === catName → activeCategory = '全部'
  → Toast "分类「{name}」已删除"
```

## Testing Notes

- Unit: `addCategory` / `removeCategory` store actions (mocked API).
- Unit: `generateCategoryColor` deterministic output.
- Integration: Backend `DELETE /categories?name=X` clears items correctly.
- Manual: Create category → sidebar updates immediately. Delete category → sidebar removes it, items lose the category, active filter resets.
