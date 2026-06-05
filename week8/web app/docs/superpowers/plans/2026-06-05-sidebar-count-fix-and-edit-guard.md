# Sidebar Count Fix & Edit Leave Guard — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix sidebar counts to always show true server-side totals for both tabs, and add an edit leave guard with a three-button confirmation dialog (save/discard/cancel).

**Architecture:** Store-driven approach — new `todoCount`/`noteCount` fields split from `totalCount` for sidebar display; `isDirty` tracked in DetailPanel and synced to store; `tryLeaveEdit()`/`resolveLeave()` in store for centralized guard; MainLayout guards all 5 navigation points and loads both tabs in parallel on category/search change.

**Tech Stack:** Vue 3 (Composition API), Pinia

---

## File Structure

| File | Responsibility |
|------|---------------|
| `stores/notes.js` | Central state: per-tab counts, dirty flag, leave guard actions; all mutations tracked here |
| `components/Sidebar.vue` | Display only: reads `store.todoCount` / `store.noteCount` |
| `components/DetailPanel.vue` | Form-level: tracks `isDirty` from edit form fields, syncs to store |
| `components/ConfirmDialog.vue` | Presentational: adds three-button mode via new props |
| `views/MainLayout.vue` | Orchestrator: guards all navigation, parallel tab loading, wires leave dialog |

---

### Task 1: Store — Add new state fields

**Files:**
- Modify: `web app/frontend/src/stores/notes.js:19-36` (state declarations)
- Modify: `web app/frontend/src/stores/notes.js:284-297` (return statement)

- [ ] **Step 1: Add new state fields after `pageSize`**

In `web app/frontend/src/stores/notes.js`, after line 36 (`const pageSize = 20`), add:

```javascript
  const todoCount = ref(0)
  const noteCount = ref(0)
  const isDirty = ref(false)
  const showLeaveConfirm = ref(false)
  const pendingLeave = ref(null)
```

- [ ] **Step 2: Export new state in return statement**

In the `return` block (starting at line 284), add `todoCount, noteCount, isDirty, showLeaveConfirm` to the returned object. Insert after `pageSize` on line 290:

```javascript
    error, currentPage, totalCount, pageSize,
    todoCount, noteCount, isDirty, showLeaveConfirm,
    loadTodos, loadNotes, loadCategories,
```

- [ ] **Step 3: Commit**

```bash
git add "web app/frontend/src/stores/notes.js"
git commit -m "feat(store): add todoCount, noteCount, isDirty, showLeaveConfirm, pendingLeave state"
```

---

### Task 2: Store — Split count tracking in loadTodos / loadNotes

**Files:**
- Modify: `web app/frontend/src/stores/notes.js:49-79`

- [ ] **Step 1: Update `loadTodos()` to set `todoCount`**

In `loadTodos()` (lines 49-63), change line 56 from `totalCount.value = res.data.count` to:

```javascript
      todos.value = res.data.results
      totalCount.value = res.data.count
      todoCount.value = res.data.count
```

Full updated function:

```javascript
  async function loadTodos() {
    isTodosLoading.value = true
    error.value = null
    try {
      const params = getListParams()
      const res = await fetchTodos(params)
      todos.value = res.data.results
      totalCount.value = res.data.count
      todoCount.value = res.data.count
    } catch (e) {
      error.value = e.response?.data?.detail || e.message || '加载待办失败'
      throw e
    } finally {
      isTodosLoading.value = false
    }
  }
```

- [ ] **Step 2: Update `loadNotes()` to set `noteCount`**

In `loadNotes()` (lines 65-79), change line 72 from `totalCount.value = res.data.count` to:

```javascript
      notes.value = res.data.results
      totalCount.value = res.data.count
      noteCount.value = res.data.count
```

Full updated function:

```javascript
  async function loadNotes() {
    isNotesLoading.value = true
    error.value = null
    try {
      const params = getListParams()
      const res = await fetchNotes(params)
      notes.value = res.data.results
      totalCount.value = res.data.count
      noteCount.value = res.data.count
    } catch (e) {
      error.value = e.response?.data?.detail || e.message || '加载笔记失败'
      throw e
    } finally {
      isNotesLoading.value = false
    }
  }
```

- [ ] **Step 3: Commit**

```bash
git add "web app/frontend/src/stores/notes.js"
git commit -m "feat(store): split totalCount into todoCount and noteCount"
```

---

### Task 3: Store — Maintain counts in add/remove operations

**Files:**
- Modify: `web app/frontend/src/stores/notes.js:100-131` (addTodo, addNote)
- Modify: `web app/frontend/src/stores/notes.js:220-244` (removeTodo, removeNote)

- [ ] **Step 1: Increment `todoCount` in `addTodo` optimistic path**

In `addTodo()` lines 100-115, add `todoCount.value++` after `totalCount.value++` on line 108:

```javascript
  async function addTodo(data) {
    const res = await createTodo(data)
    const hasFilter = activeCategory.value !== '全部' || searchQuery.value !== ''
    if (hasFilter || currentPage.value !== 1) {
      currentPage.value = 1
      await loadTodos()
    } else {
      todos.value.unshift(res.data)
      totalCount.value++
      todoCount.value++
      if (todos.value.length > pageSize) {
        todos.value.pop()
      }
    }
    return res.data
  }
```

- [ ] **Step 2: Increment `noteCount` in `addNote` optimistic path**

In `addNote()` lines 117-131, add `noteCount.value++` after `totalCount.value++` on line 125:

```javascript
  async function addNote(data) {
    const res = await createNote(data)
    const hasFilter = activeCategory.value !== '全部' || searchQuery.value !== ''
    if (hasFilter || currentPage.value !== 1) {
      currentPage.value = 1
      await loadNotes()
    } else {
      notes.value.unshift(res.data)
      totalCount.value++
      noteCount.value++
      if (notes.value.length > pageSize) {
        notes.value.pop()
      }
    }
    return res.data
  }
```

- [ ] **Step 3: Decrement `todoCount` in `removeTodo`**

In `removeTodo()` lines 220-231, add `todoCount.value--` after `totalCount.value--` on line 225:

```javascript
  async function removeTodo(id) {
    await deleteTodo(id)
    const idx = todos.value.findIndex(t => t.id === id)
    if (idx !== -1) {
      todos.value.splice(idx, 1)
      totalCount.value--
      todoCount.value--
    }
    if (todos.value.length === 0 && currentPage.value > 1) {
      currentPage.value = Math.max(1, currentPage.value - 1)
      await loadTodos()
    }
  }
```

- [ ] **Step 4: Decrement `noteCount` in `removeNote`**

In `removeNote()` lines 233-244, add `noteCount.value--` after `totalCount.value--` on line 238:

```javascript
  async function removeNote(id) {
    await deleteNote(id)
    const idx = notes.value.findIndex(n => n.id === id)
    if (idx !== -1) {
      notes.value.splice(idx, 1)
      totalCount.value--
      noteCount.value--
    }
    if (notes.value.length === 0 && currentPage.value > 1) {
      currentPage.value = Math.max(1, currentPage.value - 1)
      await loadNotes()
    }
  }
```

- [ ] **Step 5: Commit**

```bash
git add "web app/frontend/src/stores/notes.js"
git commit -m "feat(store): maintain todoCount/noteCount in add/remove operations"
```

---

### Task 4: Store — Add leave guard actions

**Files:**
- Modify: `web app/frontend/src/stores/notes.js` (add before `setActiveTab`, and update return)

- [ ] **Step 1: Add `tryLeaveEdit()` and `resolveLeave()` functions**

Insert before `setActiveTab` function (before line 265):

```javascript
  async function tryLeaveEdit() {
    if (!isDirty.value) {
      return { allowed: true, action: 'none' }
    }
    if (showLeaveConfirm.value) {
      return { allowed: false }
    }
    return new Promise((resolve) => {
      pendingLeave.value = { resolve }
      showLeaveConfirm.value = true
    })
  }

  function resolveLeave(action) {
    if (pendingLeave.value) {
      pendingLeave.value.resolve({ allowed: action !== 'cancel', action })
    }
    showLeaveConfirm.value = false
    pendingLeave.value = null
  }
```

- [ ] **Step 2: Export `tryLeaveEdit` and `resolveLeave` in return statement**

In the `return` block, add `tryLeaveEdit, resolveLeave` after `setActiveTab, setActiveCategory, setSearchQuery, setPage`:

```javascript
    setActiveTab, setActiveCategory, setSearchQuery, setPage,
    tryLeaveEdit, resolveLeave,
```

- [ ] **Step 3: Commit**

```bash
git add "web app/frontend/src/stores/notes.js"
git commit -m "feat(store): add tryLeaveEdit and resolveLeave guard actions"
```

---

### Task 5: Sidebar — Use new count fields

**Files:**
- Modify: `web app/frontend/src/components/Sidebar.vue:47-55`

- [ ] **Step 1: Change template from array `.length` to store count fields**

Replace line 48 and line 53:

```html
    <div class="sidebar-footer">
      <div class="footer-stats">
        <span class="stat-item">
          <span class="stat-count">{{ store.todoCount }}</span>
          <span class="stat-label">待办</span>
        </span>
        <span class="stat-divider">·</span>
        <span class="stat-item">
          <span class="stat-count">{{ store.noteCount }}</span>
          <span class="stat-label">笔记</span>
        </span>
      </div>
      <div class="footer-divider"></div>
      <ThemeToggle />
    </div>
```

- [ ] **Step 2: Commit**

```bash
git add "web app/frontend/src/components/Sidebar.vue"
git commit -m "fix(sidebar): use todoCount/noteCount from store instead of array length"
```

---

### Task 6: ConfirmDialog — Add three-button mode

**Files:**
- Modify: `web app/frontend/src/components/ConfirmDialog.vue:12-16` (template actions)
- Modify: `web app/frontend/src/components/ConfirmDialog.vue:24-29` (script props + emits)

- [ ] **Step 1: Add new props and emit**

Replace the script setup block (lines 23-29):

```javascript
<script setup>
defineProps({
  visible: { type: Boolean, default: false },
  message: { type: String, default: '确定执行此操作？' },
  confirmText: { type: String, default: '确定删除' },
  cancelText: { type: String, default: '取消' },
  showDiscard: { type: Boolean, default: false },
  discardText: { type: String, default: '不保存' },
})

defineEmits(['confirm', 'cancel', 'discard'])
</script>
```

- [ ] **Step 2: Update template buttons for three-button mode**

Replace the dialog-actions div (lines 13-16):

```html
          <div class="dialog-actions">
            <button v-if="showDiscard" class="btn-discard" @click="$emit('discard')">{{ discardText }}</button>
            <button class="btn-cancel" @click="$emit('cancel')">{{ cancelText }}</button>
            <button class="btn-confirm" @click="$emit('confirm')">{{ confirmText }}</button>
          </div>
```

- [ ] **Step 3: Add `.btn-discard` style**

In the `<style scoped>` block, after `.btn-cancel:hover` (after line 89), add:

```css
.btn-discard {
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

.btn-discard:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}
```

- [ ] **Step 4: Commit**

```bash
git add "web app/frontend/src/components/ConfirmDialog.vue"
git commit -m "feat(confirm-dialog): add confirmText, cancelText, showDiscard, discardText props"
```

---

### Task 7: DetailPanel — Track dirty state

**Files:**
- Modify: `web app/frontend/src/components/DetailPanel.vue:230-254` (refs, watchers)
- Modify: `web app/frontend/src/components/DetailPanel.vue:323-385` (startEdit, cancelEdit, save)

- [ ] **Step 1: Add `isDirty` ref after `newCatInput`**

After line 235 (`const newCatInput = ref(null)`), add:

```javascript
const isDirty = ref(false)
```

- [ ] **Step 2: Add watchers for dirty tracking**

After the existing `watch(() => store.selectedItem, ...)` block (ending at line 255), add:

```javascript
watch([() => editForm.value.title, () => editForm.value.content,
       () => editForm.value.category, () => editForm.value.due_date],
  () => { isDirty.value = true },
  { deep: false }
)

watch(isDirty, (val) => {
  store.isDirty = val
})
```

- [ ] **Step 3: Reset `isDirty` in `startEdit`**

In `startEdit()` (line 323), add `isDirty.value = false` after `isEditing.value = true`:

```javascript
function startEdit() {
  const item = store.selectedItem
  editForm.value = {
    title: item.title || '',
    category: item.category || '',
    content: item.content || '',
    due_date: item.due_date || '',
  }
  formErrors.value = {}
  isDirty.value = false
  isEditing.value = true
}
```

- [ ] **Step 4: Reset `isDirty` in `cancelEdit`**

In `cancelEdit()` (line 335), add `isDirty.value = false`:

```javascript
function cancelEdit() {
  isDirty.value = false
  isEditing.value = false
  formErrors.value = {}
}
```

- [ ] **Step 5: Reset `isDirty` in `save` success path**

In `save()` (lines 352-385), after `isEditing.value = false` on line 380, add `isDirty.value = false`:

```javascript
    isDirty.value = false
    isEditing.value = false
    emit('toast', { message: '保存成功', type: 'success' })
```

**Note:** `isDirty` must NOT be reset on save failure — the error path leaves it `true` so the guard re-triggers.

- [ ] **Step 6: Also reset `isDirty` in the selectedItem watcher for new-item auto-edit**

In the watcher at line 242-255, add `isDirty.value = false` in the `if (item && !item.id)` block, after `isEditing.value = true`:

```javascript
watch(() => store.selectedItem, (item) => {
  if (item && !item.id) {
    editForm.value = {
      title: item.title || '',
      category: item.category || '',
      content: item.content || '',
      due_date: item.due_date || '',
    }
    formErrors.value = {}
    isDirty.value = false
    isEditing.value = true
  } else {
    isEditing.value = false
  }
})
```

- [ ] **Step 7: Commit**

```bash
git add "web app/frontend/src/components/DetailPanel.vue"
git commit -m "feat(detail-panel): track isDirty state and sync to store"
```

---

### Task 8: MainLayout — Parallel tab loading on category/search change

**Files:**
- Modify: `web app/frontend/src/views/MainLayout.vue:117-154` (watchers and onMounted)

- [ ] **Step 1: Change category watcher to load both tabs in parallel**

Replace lines 129-143:

```javascript
let categoryDebounce = null
watch(() => store.activeCategory, () => {
  clearTimeout(categoryDebounce)
  categoryDebounce = setTimeout(async () => {
    try {
      await Promise.allSettled([
        store.loadTodos(),
        store.loadNotes()
      ])
    } catch (e) {
      showToast({ message: '加载失败', type: 'error' })
    }
  }, 150)
})
```

**Note:** `Promise.allSettled` never throws, so we can remove the try/catch or keep it for safety. The `catch` on `Promise.allSettled` is a no-op but harmless. We can simplify:

```javascript
let categoryDebounce = null
watch(() => store.activeCategory, () => {
  clearTimeout(categoryDebounce)
  categoryDebounce = setTimeout(async () => {
    await Promise.allSettled([
      store.loadTodos(),
      store.loadNotes()
    ])
  }, 150)
})
```

- [ ] **Step 2: Change tab watcher to also load both tabs for initial count sync**

Replace lines 117-127:

```javascript
watch(() => store.activeTab, async () => {
  try {
    if (store.activeTab === 'todo') {
      await store.loadTodos()
    } else {
      await store.loadNotes()
    }
  } catch (e) {
    showToast({ message: '加载失败', type: 'error' })
  }
})
```

**Note:** The tab watcher should stay as-is (load only the active tab), because tab switch is a deliberate navigation — we only need the current tab's data for display. The counts will be up-to-date from the parallel loads on category change. Actually wait — on tab switch without a category change, the other tab's count hasn't been loaded yet. But since we now load both on initial mount and on every category change, the counts will be correct. The tab switch is just for displaying the active tab's items.

Actually, the tab watcher should stay as-is per the spec. The key fix is the category watcher and the onMounted.

- [ ] **Step 3: Add `loadNotes()` to `onMounted`**

Replace lines 145-154:

```javascript
onMounted(async () => {
  try {
    await Promise.all([
      store.loadTodos(),
      store.loadNotes(),
      store.loadCategories(),
    ])
  } catch (e) {
    showToast({ message: '加载失败', type: 'error' })
  }
})
```

- [ ] **Step 4: Commit**

```bash
git add "web app/frontend/src/views/MainLayout.vue"
git commit -m "fix(main-layout): load both tabs in parallel on category change and mount"
```

---

### Task 9: MainLayout — Wire leave guard dialog and guarded close

**Files:**
- Modify: `web app/frontend/src/views/MainLayout.vue:1-25` (template)
- Modify: `web app/frontend/src/views/MainLayout.vue:27-36` (imports, refs)

- [ ] **Step 1: Add template ref for DetailPanel**

At the top of `<script setup>`, near the store declaration, add:

```javascript
const store = useNotesStore()
const detailPanelRef = ref(null)
```

- [ ] **Step 2: Add ref on DetailPanel in template**

On line 9-12, add `ref="detailPanelRef"`:

```html
    <DetailPanel
      ref="detailPanelRef"
      @toast="showToast"
      @confirm-delete="onRequestDelete"
    />
```

- [ ] **Step 3: Add leave confirmation dialog to template**

After the existing `ConfirmDialog` (line 18-23), add a second `ConfirmDialog` for the leave guard:

```html
    <ConfirmDialog
      :visible="store.showLeaveConfirm"
      message="你有未保存的更改，是否保存后再离开？"
      confirm-text="保存并离开"
      cancel-text="取消"
      :show-discard="true"
      discard-text="不保存"
      @confirm="store.resolveLeave('save')"
      @discard="store.resolveLeave('discard')"
      @cancel="store.resolveLeave('cancel')"
    />
```

- [ ] **Step 4: Add the import for `ref` (it might already be imported)**

Check line 28: `import { ref, onMounted, onUnmounted, watch } from 'vue'` — `ref` is already imported. No change needed.

- [ ] **Step 5: Commit**

```bash
git add "web app/frontend/src/views/MainLayout.vue"
git commit -m "feat(main-layout): add leave guard dialog and DetailPanel ref"
```

---

### Task 10: MainLayout — Guard all 5 navigation points

**Files:**
- Modify: `web app/frontend/src/views/MainLayout.vue:66-115` (onSelect, onCreate, onClose handler)

- [ ] **Step 1: Replace `onConfirmDelete` to also reset isDirty when delete succeeds**

In `onConfirmDelete` (line 66), after successful delete at line 77 (`store.closeDetail()`), the detail panel closes and isDirty should be irrelevant, but let's be explicit. Actually, since closeDetail nulls selectedItem which unwatches the form — no explicit reset needed.

**Important:** `DetailPanel.save()` catches errors internally and does NOT re-throw — it shows a toast and leaves `isDirty = true`. So after calling `save()` from MainLayout, we must check `store.isDirty`: if still true, save failed, and we must NOT navigate away (return early).

The guard pattern for every navigation point:

```javascript
const result = await store.tryLeaveEdit()
if (!result.allowed) return

if (result.action === 'save') {
  await detailPanelRef.value.save()
  if (store.isDirty) return   // save failed — stay on form
}
```

- [ ] **Step 2: Guard `onSelect`**

Replace `onSelect` (lines 95-101):

```javascript
async function onSelect(item, type) {
  const result = await store.tryLeaveEdit()
  if (!result.allowed) return

  if (result.action === 'save') {
    await detailPanelRef.value.save()
    if (store.isDirty) return
  }

  try {
    await store.openDetail(item.id, type)
  } catch (e) {
    showToast({ message: '加载详情失败', type: 'error' })
  }
}
```

- [ ] **Step 3: Guard `onCreate`**

Replace `onCreate` (lines 103-115):

```javascript
async function onCreate() {
  const result = await store.tryLeaveEdit()
  if (!result.allowed) return

  if (result.action === 'save') {
    await detailPanelRef.value.save()
    if (store.isDirty) return
  }

  const base = {
    title: '',
    category: '',
    content: '',
    is_completed: false,
  }
  if (store.activeTab === 'todo') {
    base.due_date = getTodayDateString()
  }
  store.selectedItem = base
  store.selectedType = store.activeTab === 'text' ? 'note' : 'todo'
}
```

- [ ] **Step 4: Guard tab watcher**

Replace the tab watcher (lines 117-127):

```javascript
watch(() => store.activeTab, async () => {
  const result = await store.tryLeaveEdit()
  if (!result.allowed) return

  if (result.action === 'save') {
    await detailPanelRef.value.save()
    if (store.isDirty) return
  }

  try {
    if (store.activeTab === 'todo') {
      await store.loadTodos()
    } else {
      await store.loadNotes()
    }
  } catch (e) {
    showToast({ message: '加载失败', type: 'error' })
  }
})
```

- [ ] **Step 5: Guard category watcher**

Replace the category watcher (lines 129-143):

```javascript
let categoryDebounce = null
watch(() => store.activeCategory, () => {
  clearTimeout(categoryDebounce)
  categoryDebounce = setTimeout(async () => {
    const result = await store.tryLeaveEdit()
    if (!result.allowed) return

    if (result.action === 'save') {
      await detailPanelRef.value.save()
      if (store.isDirty) return
    }

    await Promise.allSettled([
      store.loadTodos(),
      store.loadNotes()
    ])
  }, 150)
})
```

- [ ] **Step 6: Guard close panel — update `DetailPanel` close button behavior**

The close button in DetailPanel template calls `store.closeDetail()` directly via `@click="store.closeDetail()"`. This bypasses the guard. We need to emit close instead and handle it in MainLayout.

In `web app/frontend/src/components/DetailPanel.vue`, line 6, change:

```html
        <button class="back-btn" @click="store.closeDetail()" aria-label="关闭">
```

to:

```html
        <button class="back-btn" @click="emit('close')" aria-label="关闭">
```

Add `'close'` to the `defineEmits` in DetailPanel (line 265):

```javascript
const emit = defineEmits(['toast', 'confirm-delete', 'close'])
```

In MainLayout template, add `@close` handler on DetailPanel (line 9-12):

```html
    <DetailPanel
      ref="detailPanelRef"
      @toast="showToast"
      @confirm-delete="onRequestDelete"
      @close="onCloseDetail"
    />
```

Add `onCloseDetail` function in MainLayout script:

```javascript
async function onCloseDetail() {
  const result = await store.tryLeaveEdit()
  if (!result.allowed) return

  if (result.action === 'save') {
    await detailPanelRef.value.save()
    if (store.isDirty) return
  }

  store.closeDetail()
}
```

- [ ] **Step 7: Commit**

```bash
git add "web app/frontend/src/views/MainLayout.vue" "web app/frontend/src/components/DetailPanel.vue"
git commit -m "feat(main-layout): guard all 5 navigation points with tryLeaveEdit"
```

---

### Task 11: Typecheck

**Files:** N/A

- [ ] **Step 1: Install dependencies if needed**

```bash
cd "web app/frontend" && npm install
```

- [ ] **Step 2: Run the build to verify no compilation errors**

```bash
cd "web app/frontend" && npx vite build
```

Expected: Build succeeds with no errors.

- [ ] **Step 3: Fix any compilation errors, commit if changes needed**

---

### Task 12: Manual verification checklist

- [ ] **Count fix — initial load**: Start app, verify Sidebar shows `todoCount` and `noteCount` (not 0 for both)
- [ ] **Count fix — category switch**: Click a category, verify both counts update immediately
- [ ] **Count fix — tab switch**: Switch tabs, verify counts remain consistent
- [ ] **Leave guard — dirty**: Edit a note, change title, click a sidebar category → confirm dialog appears
- [ ] **Leave guard — cancel**: In the confirm dialog, click "取消" → stays in edit mode
- [ ] **Leave guard — discard**: In the confirm dialog, click "不保存" → navigates, edit discarded
- [ ] **Leave guard — save**: In the confirm dialog, click "保存并离开" → saves, then navigates
- [ ] **Leave guard — clean**: Edit a note, make no changes, click sidebar category → no dialog, navigates silently
- [ ] **Leave guard — close button**: Edit → click the back arrow (×) button → confirm dialog appears
- [ ] **Leave guard — new button**: Edit → click "New" button → confirm dialog appears
- [ ] **Existing flows**: Create item, update item, delete item, pagination — all still work
