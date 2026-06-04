# Category Chips + Due Date Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add category chip selector (replacing free-text input) and todo due_date field (native date input, defaults today, displays YYYY-MM-DD) to both create and edit flows.

**Architecture:** Backend adds a `due_date` DateField to the Todo model with auto-migration. Frontend replaces the category `<input>` in DetailPanel with a chip bar + "新建分类" inline input toggle, adds `<input type="date">` for todos, updates TodoItem to display due_date instead of created_at, and seeds today's date on create via MainLayout.

**Tech Stack:** Django REST Framework (backend) + Vue 3 / Pinia (frontend)

**Files modified:**
- `backend/notes/models.py` — add `due_date` field
- `backend/notes/tests.py` — add due_date test
- `frontend/src/utils/categories.js` — add `getTodayDateString()`
- `frontend/src/views/MainLayout.vue` — seed `due_date` default on create
- `frontend/src/components/TodoItem.vue` — display due_date instead of created_at
- `frontend/src/components/DetailPanel.vue` — chip bar + date input

---

### Task 1: Add `due_date` field to Todo model and create migration

**Files:**
- Modify: `backend/notes/models.py`
- Create: auto-generated migration `backend/notes/migrations/0002_*.py`

- [ ] **Step 1: Add `due_date` field to Todo model**

Add `from datetime import date` to the top of `backend/notes/models.py`:

```python
from datetime import date
from django.db import models
```

Add the `due_date` field to the `Todo` class, below `category`:

```python
class Todo(models.Model):
    CATEGORY_CHOICES = [
        ("工作", "工作"),
        ("学习", "学习"),
        ("生活", "生活"),
        ("想法", "想法"),
    ]

    title = models.CharField(max_length=200)
    content = models.TextField(blank=True, default="")
    category = models.CharField(max_length=50, blank=True, default="")
    due_date = models.DateField(null=True, blank=True, default=date.today)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

- [ ] **Step 2: Create and apply migration**

Run from the backend directory (`D:/project/cs146s/modern-software-dev-assignments/week8/web app/backend`):

```bash
python manage.py makemigrations notes
```

Expected: creates `backend/notes/migrations/0002_todo_due_date.py` (or similar name).

```bash
python manage.py migrate
```

Expected: "Applying notes.0002_todo_due_date... OK"

- [ ] **Step 3: Verify serializer picks up the new field**

Run the existing serializer test to confirm `"__all__"` includes `due_date`:

```bash
cd backend && python manage.py test notes.tests.TodoSerializerTest -v2
```

Expected: all existing tests pass.

- [ ] **Step 4: Commit**

```bash
git add backend/notes/models.py backend/notes/migrations/
git commit -m "feat: add due_date field to Todo model"
```

---

### Task 2: Add backend test for due_date

**Files:**
- Modify: `backend/notes/tests.py`

- [ ] **Step 1: Add model test for due_date default**

Add to `TodoModelTest` class:

```python
def test_due_date_defaults_to_today(self):
    from datetime import date
    todo = Todo.objects.create(title="Task with default due date")
    self.assertEqual(todo.due_date, date.today())

def test_due_date_can_be_set_explicitly(self):
    from datetime import date
    d = date(2026, 12, 25)
    todo = Todo.objects.create(title="Christmas task", due_date=d)
    self.assertEqual(todo.due_date, d)
```

- [ ] **Step 2: Add API test for creating todo with due_date**

Add to `TodoAPITest` class:

```python
def test_create_todo_with_due_date(self):
    response = self.client.post(
        "/api/v1/todos",
        {
            "title": "Scheduled Todo",
            "category": "工作",
            "due_date": "2026-12-25",
        },
        format="json",
    )
    self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    self.assertEqual(response.data["due_date"], "2026-12-25")

def test_create_todo_without_due_date_defaults_today(self):
    response = self.client.post(
        "/api/v1/todos",
        {
            "title": "No date todo",
            "category": "工作",
        },
        format="json",
    )
    self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    from datetime import date
    self.assertEqual(response.data["due_date"], str(date.today()))
```

- [ ] **Step 3: Run the new tests**

```bash
cd backend && python manage.py test notes.tests.TodoModelTest.test_due_date_defaults_to_today notes.tests.TodoModelTest.test_due_date_can_be_set_explicitly notes.tests.TodoAPITest.test_create_todo_with_due_date notes.tests.TodoAPITest.test_create_todo_without_due_date_defaults_today -v2
```

Expected: 4 tests pass.

- [ ] **Step 4: Run full test suite to verify no regressions**

```bash
cd backend && python manage.py test notes -v2
```

Expected: all tests pass.

- [ ] **Step 5: Commit**

```bash
git add backend/notes/tests.py
git commit -m "test: add tests for Todo due_date field"
```

---

### Task 3: Add `getTodayDateString()` helper

**Files:**
- Modify: `frontend/src/utils/categories.js`

- [ ] **Step 1: Add the helper function**

Add at the end of `frontend/src/utils/categories.js`:

```js
export function getTodayDateString() {
  const d = new Date()
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}
```

Use manual formatting instead of `toISOString().split('T')[0]` to avoid timezone edge cases — `new Date()` in a UTC+X timezone with `toISOString()` may return the previous day near midnight.

- [ ] **Step 2: Commit**

```bash
git add frontend/src/utils/categories.js
git commit -m "feat: add getTodayDateString() helper"
```

---

### Task 4: Update `MainLayout.onCreate()` to seed due_date default

**Files:**
- Modify: `frontend/src/views/MainLayout.vue`

- [ ] **Step 1: Import `getTodayDateString`**

Add to the import from `categories.js` in the `<script setup>` block. Currently line 29-30 only import from `../stores/notes.js`. Add the new import:

```js
import { getTodayDateString } from '../utils/categories.js'
```

- [ ] **Step 2: Update `onCreate()` to include `due_date` for todos**

Replace the `onCreate()` function (currently lines 84-93):

```js
function onCreate() {
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

- [ ] **Step 3: Commit**

```bash
git add frontend/src/views/MainLayout.vue
git commit -m "feat: seed due_date default on todo create"
```

---

### Task 5: Update TodoItem to display due_date

**Files:**
- Modify: `frontend/src/components/TodoItem.vue`

- [ ] **Step 1: Replace the date display in template**

Change line 40 from:

```html
<span class="date">{{ formatDate(todo.created_at) }}</span>
```

To:

```html
<span class="date">{{ formattedDueDate }}</span>
```

- [ ] **Step 2: Update imports and add computed property**

Replace the `formatRelativeDate` import (line 46) with `formatDate`:

```js
import { categoryColor, categoryBgColor, formatDate } from '../utils/categories.js'
```

Remove the `formatDate` function (lines 70-72) and add a computed property in the `<script setup>` block:

```js
const formattedDueDate = computed(() => {
  if (props.todo.due_date) {
    return formatDate(props.todo.due_date)
  }
  return '---'
})
```

Also add `computed` to the Vue import on line 44 — it may already be imported. Check the existing imports; if `computed` is not there, add it:

```js
import { computed } from 'vue'  // only if not already present
```

Looking at the current file, line 44: `import { useNotesStore } from '../stores/notes.js'` — there is no `computed` import yet. Add it:

```js
import { computed } from 'vue'
import { useNotesStore } from '../stores/notes.js'
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/TodoItem.vue
git commit -m "feat: display due_date in TodoItem instead of created_at"
```

---

### Task 6: Update DetailPanel — category chips + due date input

**Files:**
- Modify: `frontend/src/components/DetailPanel.vue`

This is the most complex change. It replaces the category text input with a chip bar and adds the due date date input.

- [ ] **Step 1: Add `due_date` field to `editForm` and `watch`**

In the `<script setup>` block, update `editForm` (line 182) to include `due_date`:

```js
const editForm = ref({ title: '', category: '', content: '', due_date: '' })
```

Update the `watch` on `store.selectedItem` (lines 190-202) to include `due_date`:

```js
watch(() => store.selectedItem, (item) => {
  if (item && !item.id) {
    editForm.value = {
      title: item.title || '',
      category: item.category || '',
      content: item.content || '',
      due_date: item.due_date || '',
    }
    formErrors.value = {}
    isEditing.value = true
  } else {
    isEditing.value = false
  }
})
```

- [ ] **Step 2: Add category chip state and computed**

Add these new refs and computed after `formErrors` (after line 183):

```js
const isCreatingCategory = ref(false)
const newCategoryName = ref('')
```

Add a computed for available categories. Import `PRESET_CATEGORIES` from categories.js:

```js
import { categoryColor, categoryBgColor, formatDate, PRESET_CATEGORIES } from '../utils/categories.js'
```

Add the computed:

```js
const availableCategories = computed(() => {
  const presets = PRESET_CATEGORIES.filter(c => c !== '全部')
  const custom = store.categories.filter(c => !PRESET_CATEGORIES.includes(c))
  return [...presets, ...custom]
})
```

- [ ] **Step 3: Add chip helper functions**

Add these functions in the `<script setup>` block, before `startEdit()`:

```js
function selectCategory(cat) {
  isCreatingCategory.value = false
  newCategoryName.value = ''
  editForm.value.category = cat
}

function startNewCategory() {
  isCreatingCategory.value = true
  newCategoryName.value = ''
}

function confirmNewCategory() {
  const trimmed = newCategoryName.value.trim()
  if (trimmed) {
    editForm.value.category = trimmed
  }
  isCreatingCategory.value = false
  newCategoryName.value = ''
}

function cancelNewCategory() {
  isCreatingCategory.value = false
  newCategoryName.value = ''
}
```

- [ ] **Step 4: Update `startEdit()` to include `due_date`**

Update `startEdit()` (lines 219-228) to include `due_date`:

```js
function startEdit() {
  const item = store.selectedItem
  editForm.value = {
    title: item.title || '',
    category: item.category || '',
    content: item.content || '',
    due_date: item.due_date || '',
  }
  formErrors.value = {}
  isEditing.value = true
}
```

- [ ] **Step 5: Update `save()` to include `due_date`**

In the `save()` function (lines 247-277), update the `data` object to include `due_date`:

```js
const data = {
  title: editForm.value.title.trim(),
  category: editForm.value.category.trim(),
  content: editForm.value.content,
}
if (store.selectedType === 'todo') {
  data.due_date = editForm.value.due_date || null
}
```

- [ ] **Step 6: Replace category input with chip bar in template**

In the template, find the edit mode's category form group (lines 128-136):

```html
<div class="form-group">
  <label class="form-label">分类</label>
  <input
    v-model="editForm.category"
    class="form-input"
    placeholder="例如：工作、学习、生活…"
    maxlength="50"
  />
</div>
```

Replace with:

```html
<div class="form-group">
  <label class="form-label">分类</label>
  <div class="category-chip-bar">
    <button
      type="button"
      class="category-chip"
      :class="{ selected: editForm.category === '' && !isCreatingCategory }"
      @click="selectCategory('')"
    >无分类</button>
    <button
      v-for="cat in availableCategories"
      :key="cat"
      type="button"
      class="category-chip"
      :class="{ selected: editForm.category === cat }"
      :style="editForm.category === cat ? chipActiveStyle(cat) : {}"
      @click="selectCategory(cat)"
    >{{ cat }}</button>
    <template v-if="!isCreatingCategory">
      <button
        type="button"
        class="category-chip new-category-chip"
        @click="startNewCategory"
      >＋ 新建分类</button>
    </template>
    <input
      v-else
      ref="newCatInput"
      v-model="newCategoryName"
      type="text"
      class="new-category-input"
      placeholder="输入新分类…"
      maxlength="50"
      @keydown.enter="confirmNewCategory"
      @blur="cancelNewCategory"
    />
  </div>
</div>
```

- [ ] **Step 7: Add due date input in template**

After the category form group, add (it is placed before the content field):

```html
<div v-if="store.selectedType === 'todo'" class="form-group">
  <label class="form-label">截止日期</label>
  <input
    v-model="editForm.due_date"
    type="date"
    class="form-input"
  />
</div>
```

- [ ] **Step 8: Add chip helper function**

Add this function in `<script setup>` for the active chip styling:

```js
function chipActiveStyle(cat) {
  return {
    borderColor: categoryColor(cat),
    background: categoryBgColor(cat),
    color: categoryColor(cat),
  }
}
```

- [ ] **Step 9: Add auto-focus ref and watcher for new category input**

Add a template ref for the new category input and a watcher to auto-focus it. Add the ref:

```js
const newCatInput = ref(null)
```

Add a watcher (after the selectedItem watcher):

```js
watch(isCreatingCategory, (val) => {
  if (val) {
    // Focus after DOM update
    setTimeout(() => {
      newCatInput.value?.focus()
    }, 50)
  }
})
```

- [ ] **Step 10: Add CSS for chip bar and date input**

Add these new styles inside the `<style scoped>` block:

```css
/* ── Category Chip Bar ── */
.category-chip-bar {
  display: flex;
  gap: var(--space-xs);
  flex-wrap: wrap;
  align-items: center;
}

.category-chip {
  padding: 4px 12px;
  border-radius: var(--radius-md);
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  border: 1px solid var(--border);
  background: var(--bg-surface);
  color: var(--text-muted);
  transition: all var(--duration-fast) var(--ease-out);
}

.category-chip:hover {
  border-color: var(--border-focus);
  color: var(--text-secondary);
}

.category-chip.selected {
  font-weight: 600;
}

.new-category-chip {
  border-style: dashed;
  color: var(--text-muted);
}

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

- [ ] **Step 11: Commit**

```bash
git add frontend/src/components/DetailPanel.vue
git commit -m "feat: add category chip bar and due date input to DetailPanel"
```

---

### Task 7: Manual verification checklist

- [ ] **Step 1: Start backend and frontend**

```bash
# Terminal 1 — backend
cd backend && python manage.py runserver

# Terminal 2 — frontend (in another shell)
cd frontend && npm run dev
```

- [ ] **Step 2: Verify category chips on create**
  - Click "新建" on todo tab
  - Confirm category chips appear (无分类, 工作, 学习, 生活, 想法)
  - Click a chip — it highlights
  - Click "＋ 新建分类" — it expands to a text input
  - Type a new category name and press Enter — it becomes selected
  - Click "无分类" — selection clears

- [ ] **Step 3: Verify due date on todo create**
  - Click "新建" on todo tab
  - Confirm due date input shows today's date (e.g., 2026-06-04)
  - Change the date using the picker
  - Fill title and save
  - Confirm the todo appears in list with the selected date

- [ ] **Step 4: Verify due date does NOT appear for notes**
  - Switch to 笔记 tab
  - Click "新建"
  - Confirm no due date field appears
  - Confirm category chips work the same

- [ ] **Step 5: Verify edit mode**
  - Click an existing todo to open detail
  - Click the edit button
  - Confirm due date field shows the saved value
  - Change category via chips and save
  - Confirm changes persist

- [ ] **Step 6: Verify existing todos without due_date**
  - If any todos exist without `due_date`, they should display `---` in the list
