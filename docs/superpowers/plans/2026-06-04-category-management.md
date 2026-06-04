# Category Management Improvements — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add real-time category creation (with save button) and category deletion (with confirmation dialog) to the web app.

**Architecture:** Backend gains a `DELETE /api/v1/categories` endpoint that clears a category from all items. Frontend store gains `addCategory`/`removeCategory` actions with a `deletedCategories` ref for session-memory. `DetailPanel` gets a save button beside the new-category input; `Sidebar` gets per-category delete buttons.

**Tech Stack:** Django REST Framework (backend), Vue 3 + Pinia (frontend), Axios (API client)

---

### Task 1: Backend — Add DELETE /api/v1/categories endpoint

**Files:**
- Modify: `backend/notes/views.py`
- Modify: `backend/notes/urls.py`

- [ ] **Step 1: Add CategoryEditView to views.py**

Add after the existing `CategoryListView` class in `urls.py`, or add a new view class. Since `urls.py` currently defines `CategoryListView` inline, add `CategoryEditView` there too:

In `backend/notes/urls.py`, add this import at the top:
```python
from rest_framework import status
```

Then add this class after `CategoryListView`:
```python
class CategoryEditView(APIView):
    def delete(self, request):
        name = request.query_params.get("name", "")
        if not name:
            return Response(
                {"detail": "缺少分类名称参数"}, status=status.HTTP_400_BAD_REQUEST
            )
        todo_count = Todo.objects.filter(category=name).update(category="")
        note_count = Note.objects.filter(category=name).update(category="")
        total = todo_count + note_count
        return Response({"deleted": name, "cleared": total})
```

- [ ] **Step 2: Register the route in urlpatterns**

Change `urlpatterns` from:
```python
urlpatterns = router.urls + [
    path("categories", CategoryListView.as_view(), name="categories"),
]
```
to:
```python
urlpatterns = router.urls + [
    path("categories", CategoryListView.as_view(), name="categories"),
    path("categories/delete", CategoryEditView.as_view(), name="category-delete"),
]
```

- [ ] **Step 3: Add backend tests**

Add to `backend/notes/tests.py` after the existing `CategoryAPITest` class:

```python
class CategoryDeleteAPITest(APITestCase):
    def setUp(self):
        Todo.objects.create(title="Work Todo", category="工作")
        Todo.objects.create(title="Another Work Todo", category="工作")
        Note.objects.create(title="Work Note", category="工作")
        Todo.objects.create(title="Study Todo", category="学习")

    def test_delete_category_clears_items(self):
        response = self.client.delete("/api/v1/categories/delete?name=工作")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["deleted"], "工作")
        self.assertEqual(response.data["cleared"], 3)

    def test_deleted_category_items_now_have_empty_category(self):
        self.client.delete("/api/v1/categories/delete?name=工作")
        from notes.models import Todo, Note
        self.assertEqual(Todo.objects.filter(category="工作").count(), 0)
        self.assertEqual(Note.objects.filter(category="工作").count(), 0)
        self.assertEqual(Todo.objects.filter(category="").count(), 2)

    def test_delete_category_only_affects_target(self):
        self.client.delete("/api/v1/categories/delete?name=工作")
        self.assertEqual(Todo.objects.filter(category="学习").count(), 1)

    def test_delete_missing_name_returns_400(self):
        response = self.client.delete("/api/v1/categories/delete")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_nonexistent_category_succeeds_with_zero(self):
        response = self.client.delete("/api/v1/categories/delete?name=不存在")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["cleared"], 0)
```

- [ ] **Step 4: Run backend tests**

```bash
cd backend && python manage.py test notes.tests.CategoryDeleteAPITest -v 2
```

- [ ] **Step 5: Commit**

```bash
git add backend/notes/urls.py backend/notes/tests.py
git commit -m "feat: add DELETE /api/v1/categories/delete endpoint"
```

---

### Task 2: Frontend Utility — Add color generation functions

**Files:**
- Modify: `frontend/src/utils/categories.js`

- [ ] **Step 1: Add hashToHsl and color generation functions**

Add to the end of `frontend/src/utils/categories.js`:

```javascript
function hashString(str) {
  let hash = 0
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash)
    hash = hash & hash // Convert to 32bit integer
  }
  return Math.abs(hash)
}

export function generateCategoryColor(name) {
  const hash = hashString(name)
  const hue = hash % 360
  return `hsl(${hue}, 30%, 40%)`
}

export function generateCategoryBgColor(name) {
  const hash = hashString(name)
  const hue = hash % 360
  return `hsl(${hue}, 30%, 92%)`
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/utils/categories.js
git commit -m "feat: add generateCategoryColor/BgColor with deterministic hashing"
```

---

### Task 3: Frontend API — Add deleteCategory function

**Files:**
- Modify: `frontend/src/api/index.js`

- [ ] **Step 1: Add deleteCategory export**

Add before `export default api`:

```javascript
export function deleteCategory(name) {
  return api.delete('/categories/delete', { params: { name } })
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/api/index.js
git commit -m "feat: add deleteCategory API function"
```

---

### Task 4: Frontend Store — Add addCategory, removeCategory, deletedCategories

**Files:**
- Modify: `frontend/src/stores/notes.js`

- [ ] **Step 1: Add deletedCategories ref**

After `const error = ref(null)`, add:
```javascript
const deletedCategories = ref([])
```

- [ ] **Step 2: Add addCategory action**

After `loadCategories`, add:
```javascript
function addCategory(name) {
  if (name && !categories.value.includes(name)) {
    categories.value.push(name)
    // Remove from deletedCategories if it was previously deleted this session
    const idx = deletedCategories.value.indexOf(name)
    if (idx !== -1) {
      deletedCategories.value.splice(idx, 1)
    }
  }
}
```

- [ ] **Step 3: Add removeCategory action**

After `addCategory`, add:
```javascript
async function removeCategory(name) {
  await deleteCategory(name)
  const idx = categories.value.indexOf(name)
  if (idx !== -1) {
    categories.value.splice(idx, 1)
  }
  if (!deletedCategories.value.includes(name)) {
    deletedCategories.value.push(name)
  }
  if (activeCategory.value === name) {
    activeCategory.value = '全部'
    if (activeTab.value === 'todo') {
      await loadTodos()
    } else {
      await loadNotes()
    }
  }
}
```

- [ ] **Step 4: Update the import line to include deleteCategory**

Change:
```javascript
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
} from '../api/index.js'
```
Add `deleteCategory`:
```javascript
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
} from '../api/index.js'
```

- [ ] **Step 5: Add to return statement**

Add `deletedCategories`, `addCategory`, `removeCategory` to the returned object:
```javascript
return {
  todos, notes, categories, deletedCategories,
  activeTab, activeCategory, searchQuery,
  selectedItem, selectedType,
  isTodosLoading, isNotesLoading, isDetailLoading,
  error, currentPage, totalCount, pageSize,
  loadTodos, loadNotes, loadCategories,
  addTodo, addNote, addCategory,
  openDetail, closeDetail,
  toggleTodoComplete,
  saveTodoEdit, saveNoteEdit,
  removeTodo, removeNote, removeCategory,
  setActiveTab, setActiveCategory, setSearchQuery, setPage,
}
```

- [ ] **Step 6: Commit**

```bash
git add frontend/src/stores/notes.js
git commit -m "feat: add addCategory and removeCategory store actions"
```

---

### Task 5: Frontend — Update DetailPanel.vue with save button + store integration

**Files:**
- Modify: `frontend/src/components/DetailPanel.vue`

- [ ] **Step 1: Update the new-category input area in the template**

Replace this block in the category chip bar (lines 152-164):
```html
<input
  v-else
  ref="newCatInput"
  v-model="newCategoryName"
  type="text"
  class="new-category-input"
  placeholder="输入新分类…"
  maxlength="50"
  @keydown.enter.prevent="confirmNewCategory"
  @blur="confirmNewCategory"
  @keydown.escape.prevent="cancelNewCategory"
/>
```
With:
```html
<div v-else class="new-category-row">
  <input
    ref="newCatInput"
    v-model="newCategoryName"
    type="text"
    class="new-category-input"
    placeholder="输入新分类…"
    maxlength="50"
    @keydown.enter.prevent="saveNewCategory"
    @keydown.escape.prevent="cancelNewCategory"
  />
  <button
    type="button"
    class="new-category-save-btn"
    :disabled="!newCategoryName.trim()"
    @click="saveNewCategory"
    aria-label="保存分类"
  >
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
      <path d="M11 4l-5 5-3-3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
  </button>
</div>
```

- [ ] **Step 2: Update the script — import has moved, update confirmNewCategory → saveNewCategory**

Replace the `confirmNewCategory` function:
```javascript
function confirmNewCategory() {
  const trimmed = newCategoryName.value.trim()
  if (trimmed) {
    editForm.value.category = trimmed
  }
  isCreatingCategory.value = false
  newCategoryName.value = ''
}
```
With:
```javascript
function saveNewCategory() {
  const trimmed = newCategoryName.value.trim()
  if (!trimmed) {
    isCreatingCategory.value = false
    newCategoryName.value = ''
    return
  }
  store.addCategory(trimmed)
  editForm.value.category = trimmed
  isCreatingCategory.value = false
  newCategoryName.value = ''
}
```

- [ ] **Step 3: Add CSS for the new save button row**

Add after the `.new-category-input` style block:
```css
.new-category-row {
  display: flex;
  align-items: center;
  gap: 4px;
}

.new-category-input {
  width: 110px;
  padding: 4px 8px;
  border: 2px solid var(--accent);
  border-radius: var(--radius-md);
  font-size: 0.75rem;
  color: var(--text-primary);
  background: var(--bg-surface);
  outline: none;
  box-shadow: 0 0 0 3px var(--accent-soft);
  box-sizing: border-box;
}

.new-category-save-btn {
  width: 28px;
  height: 28px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--accent);
  color: var(--text-inverse);
  border: none;
  cursor: pointer;
  flex-shrink: 0;
  transition: all var(--duration-fast) var(--ease-out);
}

.new-category-save-btn:hover:not(:disabled) {
  background: var(--accent-hover);
}

.new-category-save-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
```

- [ ] **Step 4: Remove the old standalone `.new-category-input` style**

The original `.new-category-input` is now inside `.new-category-row`, so update the CSS. The old block:
```css
.new-category-input {
  width: 130px;
  padding: 4px 8px;
  border: 2px solid var(--accent);
  border-radius: var(--radius-md);
  font-size: 0.75rem;
  color: var(--text-primary);
  background: var(--bg-surface);
  outline: none;
  box-shadow: 0 0 0 3px var(--accent-soft);
  box-sizing: border-box;
}
```
Replace with the `.new-category-row` block and the updated `.new-category-input` shown above.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/DetailPanel.vue
git commit -m "feat: add save button to new-category input, integrate store.addCategory"
```

---

### Task 6: Frontend — Update Sidebar.vue with delete buttons + deleted filter

**Files:**
- Modify: `frontend/src/components/Sidebar.vue`

- [ ] **Step 1: Update displayCategories to filter deleted**

Replace:
```javascript
const displayCategories = computed(() => {
  const custom = store.categories.filter(c => !PRESET_CATEGORIES.includes(c))
  return [...PRESET_CATEGORIES, ...custom]
})
```
With:
```javascript
const displayCategories = computed(() => {
  const custom = store.categories.filter(c => !PRESET_CATEGORIES.includes(c))
  return [...PRESET_CATEGORIES, ...custom].filter(c => !store.deletedCategories.includes(c))
})
```

- [ ] **Step 2: Add delete button to each nav-item (except "全部")**

Replace the nav-item button block:
```html
<button
  v-for="cat in displayCategories"
  :key="cat"
  class="nav-item"
  :class="{ active: store.activeCategory === cat }"
  @click="store.setActiveCategory(cat)"
>
  <span class="nav-dot" :class="{ filled: store.activeCategory === cat }"></span>
  <span class="nav-label">{{ cat }}</span>
  <span v-if="store.activeCategory === cat" class="nav-indicator"></span>
</button>
```
With:
```html
<button
  v-for="cat in displayCategories"
  :key="cat"
  class="nav-item"
  :class="{ active: store.activeCategory === cat }"
  @click="store.setActiveCategory(cat)"
>
  <span class="nav-dot" :class="{ filled: store.activeCategory === cat }"></span>
  <span class="nav-label">{{ cat }}</span>
  <span v-if="store.activeCategory === cat" class="nav-indicator"></span>
  <button
    v-if="cat !== '全部'"
    class="nav-delete-btn"
    @click.stop="emit('delete-category', cat)"
    aria-label="删除分类"
    title="删除分类"
  >
    <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
      <path d="M3 3l6 6M9 3l-6 6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
    </svg>
  </button>
</button>
```

- [ ] **Step 3: Add the emit declaration**

Add at the top of `<script setup>`:
```javascript
const emit = defineEmits(['delete-category'])
```

- [ ] **Step 4: Add CSS for the delete button**

Add after the `.nav-indicator` animation block:
```css
.nav-delete-btn {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  opacity: 0;
  transition: all var(--duration-fast) var(--ease-out);
  border: none;
  background: transparent;
  cursor: pointer;
  padding: 0;
}

.nav-item:hover .nav-delete-btn {
  opacity: 1;
}

.nav-delete-btn:hover {
  background: var(--error-bg);
  color: var(--error);
}
```

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/Sidebar.vue
git commit -m "feat: add category delete button to sidebar"
```

---

### Task 7: Frontend — Update MainLayout.vue to handle category delete

**Files:**
- Modify: `frontend/src/views/MainLayout.vue`

- [ ] **Step 1: Listen for delete-category on Sidebar**

Change `<Sidebar />` to:
```html
<Sidebar @delete-category="onRequestDeleteCategory" />
```

- [ ] **Step 2: Add pendingDeleteCategory state**

After `const pendingDelete = ref(null)`, add:
```javascript
const pendingDeleteCategory = ref(null)
```

- [ ] **Step 3: Add onRequestDeleteCategory handler**

After `onRequestDelete`, add:
```javascript
function onRequestDeleteCategory(name) {
  pendingDeleteCategory.value = name
  confirmMessage.value = `确定要删除分类「${name}」吗？所有属于该分类的条目将变为无分类状态。`
  showConfirm.value = true
}
```

- [ ] **Step 4: Update onConfirmDelete to handle category deletion**

Replace:
```javascript
async function onConfirmDelete() {
  showConfirm.value = false
  if (!pendingDelete.value) return
  const { item, type } = pendingDelete.value
  try {
    if (type === 'todo') {
      await store.removeTodo(item.id)
    } else {
      await store.removeNote(item.id)
    }
    store.closeDetail()
    showToast({ message: '删除成功', type: 'success' })
  } catch (e) {
    showToast({ message: '删除失败', type: 'error' })
  }
  pendingDelete.value = null
}
```
With:
```javascript
async function onConfirmDelete() {
  showConfirm.value = false
  if (pendingDelete.value) {
    const { item, type } = pendingDelete.value
    try {
      if (type === 'todo') {
        await store.removeTodo(item.id)
      } else {
        await store.removeNote(item.id)
      }
      store.closeDetail()
      showToast({ message: '删除成功', type: 'success' })
    } catch (e) {
      showToast({ message: '删除失败', type: 'error' })
    }
    pendingDelete.value = null
    return
  }
  if (pendingDeleteCategory.value) {
    try {
      await store.removeCategory(pendingDeleteCategory.value)
      showToast({ message: `分类「${pendingDeleteCategory.value}」已删除`, type: 'success' })
    } catch (e) {
      showToast({ message: '删除分类失败', type: 'error' })
    }
    pendingDeleteCategory.value = null
  }
}
```

- [ ] **Step 5: Commit**

```bash
git add frontend/src/views/MainLayout.vue
git commit -m "feat: wire up category deletion in MainLayout"
```

---

### Task 8: Run full test suite and verify

- [ ] **Step 1: Run backend tests**

```bash
cd backend && python manage.py test notes -v 2
```

- [ ] **Step 2: Typecheck frontend**

```bash
cd frontend && npx vue-tsc --noEmit 2>&1 | head -20
```

- [ ] **Step 3: Verify all tests pass, address any failures**

- [ ] **Step 4: Final commit if any fixes were made**

```bash
git add . && git commit -m "chore: final adjustments after full test run"
```
