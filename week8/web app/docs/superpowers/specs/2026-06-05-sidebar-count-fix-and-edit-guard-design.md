# Sidebar Count Fix & Edit Leave Guard — Design Spec

**Date:** 2026-06-05
**Status:** draft

## Problem Statement

### Bug: Sidebar counts out of sync across tabs

The bottom-left sidebar displays counts for notes and todos using `store.todos.length` and `store.notes.length` — the length of the locally loaded page array (max 20 items), not the true server-side total. When a category is selected, only the active tab's data is reloaded; the inactive tab's array stays stale (or empty). This means the count is only correct for the currently active tab, and incorrect for the other until the user manually switches tabs.

### Feature: Edit leave guard

When editing a note or todo, there is no protection against leaving the edit form. Clicking another list item, switching tabs, switching categories, closing the detail panel, or clicking "New" silently discards the edit form with no warning. Users can lose unsaved work.

## Design

### Architecture overview

```
┌──────────────────────────────────────────────────────────┐
│ MainLayout.vue (orchestrator)                            │
│                                                          │
│  All navigation entry points call tryLeaveEdit() first:  │
│  - close panel    - select item    - switch tab           │
│  - switch category  - new button                         │
│                                                          │
│  Category/search watcher: always loads both tabs in      │
│  parallel via Promise.allSettled                         │
└──────┬───────────────┬────────────────┬──────────────────┘
       │               │                │
       ▼               ▼                ▼
┌──────────────┐ ┌───────────┐ ┌──────────────────┐
│ Sidebar.vue  │ │ DetailPanel│ │ stores/notes.js  │
│              │ │            │ │                  │
│ Reads from   │ │ Tracks    │ │ todoCount        │
│ todoCount /  │ │ isDirty   │ │ noteCount        │
│ noteCount    │ │ syncs to  │ │ isDirty          │
│              │ │ store     │ │ showLeaveConfirm │
│              │ │           │ │ pendingLeave     │
│              │ │           │ │ tryLeaveEdit()   │
│              │ │           │ │ resolveLeave()   │
└──────────────┘ └───────────┘ └──────────────────┘
```

### Files changed

| File | Type | Summary |
|------|------|---------|
| `stores/notes.js` | Modify | New state: `todoCount`, `noteCount`, `isDirty`, `showLeaveConfirm`, `pendingLeave`. New action: `tryLeaveEdit()`, `resolveLeave()`. Modified: `loadTodos()`, `loadNotes()` update split counts. |
| `components/Sidebar.vue` | Modify | Count display switches from array `.length` to store count fields. |
| `views/MainLayout.vue` | Modify | All 5 navigation entry points guard with `tryLeaveEdit()`. Category & search watchers load both tabs in parallel. `onMounted` loads both tabs + categories. |
| `components/DetailPanel.vue` | Modify | Tracks `isDirty` via form field watcher. Syncs dirty state to store. Resets on save, cancel, and edit start. |

### Files NOT changed

- `api/index.js` — API layer unchanged
- `TodoList.vue`, `NoteCards.vue`, `ContentArea.vue`, `TopBar.vue` — UI components unchanged; events continue to bubble up to MainLayout
- `ConfirmDialog.vue` — reused as-is
- `Pagination.vue`, `Toast.vue`, `ThemeToggle.vue`, `App.vue`, `router/index.js`, `main.js` — no changes

---

## Feature 1: Sidebar Count Fix

### Store changes (`stores/notes.js`)

New state fields:

```javascript
todoCount: 0,   // true server-side total for todos
noteCount: 0,   // true server-side total for notes
```

`loadTodos()` assigns `this.todoCount = res.data.count`.
`loadNotes()` assigns `this.noteCount = res.data.count`.

Existing `totalCount` is preserved for pagination logic. `todoCount`/`noteCount` are the authoritative values for display.

### Sidebar changes (`components/Sidebar.vue`)

From `store.todos.length` / `store.notes.length` to `store.todoCount` / `store.noteCount`.

### Parallel loading on category/search change (`views/MainLayout.vue`)

Category watcher (was: load current tab only, now: load both):

```javascript
watch(() => store.activeCategory, async () => {
  await Promise.allSettled([
    store.loadTodos(),
    store.loadNotes()
  ])
}, { debounce: 150 })
```

Search watcher: same change to parallel both-tab loading.

### Initial load (`MainLayout.vue` onMounted)

```javascript
// Was: loadTodos + loadCategories
// Now: loadTodos + loadNotes + loadCategories — all in parallel
await Promise.all([
  store.loadTodos(),
  store.loadNotes(),
  store.loadCategories()
])
```

### Error tolerance

Use `Promise.allSettled` for parallel loads so one tab's failure does not prevent the other from updating. If a fetch fails, `catch` inside the store action keeps the previous count value (no NaN/undefined).

---

## Feature 2: Edit Leave Guard

### Dirty tracking (`DetailPanel.vue`)

A `ref` `isDirty` starts `false` on entering edit mode. A watcher on the edit form fields (`title`, `content`, `category`, `dueDate`) sets it to `true` on any change. `isDirty` is reset to `false` on:

- Entering edit mode (`startEdit()`)
- Successful save (`save()` success path)
- Cancel (`cancelEdit()`)

`isDirty` is synced to `store.isDirty` via a watcher so MainLayout can read it.

### Leave guard (`stores/notes.js`)

New state fields:

```javascript
isDirty: false,
showLeaveConfirm: false,
pendingLeave: null,  // { resolve: Function }
```

`tryLeaveEdit()` — called by MainLayout before any navigation:

- If `isDirty` is `false`, resolves immediately with `{ allowed: true, action: 'none' }`.
- If `isDirty` is `true`, sets `showLeaveConfirm = true` and returns a Promise. The Promise is resolved by `resolveLeave(action)`.
- Re-entrancy guard: if `showLeaveConfirm` is already `true`, returns `{ allowed: false }` immediately.

`resolveLeave(action)` — called when user clicks a button in the confirm dialog:

- `'save'` → resolves `{ allowed: true, action: 'save' }`
- `'discard'` → resolves `{ allowed: true, action: 'discard' }`
- `'cancel'` → resolves `{ allowed: false, action: 'cancel' }`
- Cleans up: `showLeaveConfirm = false`, `pendingLeave = null`

### Confirm dialog content

Reuses the existing `ConfirmDialog.vue` component, triggered by `store.showLeaveConfirm` in `MainLayout.vue`:

```
Title: 未保存的更改
Message: 你有未保存的更改，是否保存后再离开？
Buttons: [保存并离开] [不保存] [取消]
```

### Guarded navigation points (all in `MainLayout.vue`)

All 5 entry points wrap their navigation logic:

```javascript
async function guardedNavigate(targetAction) {
  const result = await store.tryLeaveEdit()
  if (!result.allowed) return

  if (result.action === 'save') {
    await detailPanelRef.value.save()
  }

  targetAction()
}
```

| # | Trigger | Handler |
|---|---------|---------|
| 1 | Close panel (`@close`) | `onCloseDetail()` |
| 2 | Select item (`@select`) | `onSelectItem(id, type)` |
| 3 | Switch tab (`@tab-change`) | `onTabChange(tab)` |
| 4 | Switch category (watcher) | Category watcher body |
| 5 | New button (`@create`) | `onCreate(type)` |

---

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| New item, no fields touched | `isDirty` stays `false` — no confirm dialog, leave silently |
| Edit existing item, no changes | `isDirty` stays `false` — no confirm dialog |
| Save fails (network error) | `isDirty` stays `true`; confirm dialog re-appears on next leave attempt |
| "Discard" clicked | Form discarded, `isDirty` reset, navigation proceeds |
| "Cancel" clicked | Navigation aborted, user stays in edit mode |
| Rapid double-click on navigation | Re-entrancy guard prevents duplicate dialogs |
| Parallel load: one tab fails | `Promise.allSettled` — failed tab keeps previous count; no crash |

## Estimated scope

~90 lines of net change across 4 files. No new dependencies. No API changes.

## Testing plan

1. **Count fix**: Start app → verify both counts show immediately. Switch category → both counts update. Switch tab → counts remain consistent.
2. **Leave guard — dirty**: Edit a note, change title, click sidebar category → confirm dialog appears. Click "Cancel" → stays in edit. Click "Discard" → navigates. Click "Save" → saves then navigates.
3. **Leave guard — clean**: Edit a note, make no changes, click sidebar category → no dialog, navigates silently.
4. **Existing flows**: Create item, update item, delete item, pagination — all continue to work unchanged.
