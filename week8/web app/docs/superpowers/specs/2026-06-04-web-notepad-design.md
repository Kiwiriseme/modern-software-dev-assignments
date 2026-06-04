# 网页记事本 (Web Notepad) — Design Spec

## Overview

A note-taking and todo management web app with Vue3 frontend and Django backend. Single-user mode (no auth). Users create/manage todos and text notes, organized by categories.

**Stack:** Vue3 + Vite + Pinia + Django + Django REST Framework + SQLite
**Assignment context:** CS146S Week 8 — version using a non-JS language (Django) backend.

---

## Data Model

### Todo
| Field | Type | Notes |
|-------|------|-------|
| id | AutoField (PK) | |
| title | CharField(max_length=200) | |
| content | TextField(blank=True, default="") | Optional description / notes |
| category | CharField(max_length=50) | Plain CharField (no Django choices); stripped on save |
| is_completed | BooleanField(default=False) | |
| created_at | DateTimeField(auto_now_add) | |
| updated_at | DateTimeField(auto_now) | |

### Note
| Field | Type | Notes |
|-------|------|-------|
| id | AutoField (PK) | |
| title | CharField(max_length=200) | |
| content | TextField(blank=True) | Markdown content |
| category | CharField(max_length=50) | Plain CharField (no Django choices); stripped on save |
| created_at | DateTimeField(auto_now_add) | |
| updated_at | DateTimeField(auto_now) | |

### Backend Validation
- **title**: non-empty, max 200 chars (validated in serializer)
- **content**: max 10000 chars (validated in serializer)
- **category**: max 50 chars, auto `strip()` in serializer's `validate_category`
- **is_completed**: boolean, default false

### Category Handling
- Backend: plain CharField — accepts any string. Category values are `strip()`-ed on save to prevent whitespace duplicates.
- Frontend sidebar: shows preset categories (全部/工作/学习/生活/想法) + dynamically lists any additional categories found via `GET /api/v1/categories`.
- User adds a custom category by typing a new name in the category field when creating/editing a note. No separate "add category" flow.

Todo and Note are independent models with separate API endpoints. Category is a plain CharField (no separate Category table).

---

## API Design

Base: `/api/v1/`
Router: `DefaultRouter` with `trailing_slash=False`

### Todo Endpoints
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/todos` | List (query: ?category=&q=&page=&page_size=) |
| POST | `/api/v1/todos` | Create |
| GET | `/api/v1/todos/:id` | Detail |
| PUT | `/api/v1/todos/:id` | Full update |
| PATCH | `/api/v1/todos/:id` | Partial update (e.g. toggle complete) |
| DELETE | `/api/v1/todos/:id` | Delete |

### Note Endpoints
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/notes` | List (query: ?category=&q=&page=&page_size=) |
| POST | `/api/v1/notes` | Create |
| GET | `/api/v1/notes/:id` | Detail |
| PUT | `/api/v1/notes/:id` | Full update |
| PATCH | `/api/v1/notes/:id` | Partial update |
| DELETE | `/api/v1/notes/:id` | Delete |

### Category Endpoint
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/categories` | Returns deduplicated, sorted list of all category strings from both Todo and Note tables |

### Search Scope
- **Todo**: `?q=` searches title and content
- **Note**: `?q=` searches title and content

### Pagination
- Default: `?page=1&page_size=20`
- Backend: DRF `PageNumberPagination` with `max_page_size = 100`
- Response format: `{ count: <total>, next: <url|null>, previous: <url|null>, results: [...] }`

### Backend Stack
- **View:** Two `ModelViewSet` classes (TodoViewSet, NoteViewSet) + one `APIView` or action for categories
- **Serializer:** Two `ModelSerializer` classes (TodoSerializer, NoteSerializer)
- **Router:** `DefaultRouter` registering both ViewSets
- **Filtering:** Custom `get_queryset` supporting `category`, `q` (search title+content), and DRF pagination

### Data Flow (Backend)
```
urls.py (Router) → views.py (ViewSet) → serializers.py (ModelSerializer) → models.py (SQLite)
```

---

## Frontend Design

### Routes
Single-page app, one route:
| Path | Component | Description |
|------|-----------|-------------|
| `/` | MainLayout.vue | Three-column layout |

Tab switching (TODO/text) and category filtering are driven by Pinia store state, not URL.

### Component Tree
```
App.vue
├── MainLayout.vue              # 3-column flex container
│   ├── Sidebar.vue             # 200px fixed width
│   │   ├── Category nav items  # 全部/工作/学习/生活/想法 + custom
│   │   └── Settings button (decorative)
│   ├── ContentArea.vue         # flex: 1
│   │   ├── TopBar.vue          # Search + TabSwitch + New button
│   │   ├── TodoList.vue        # v-if activeTab === 'todo'
│   │   │   └── TodoItem.vue    # checkbox + title + category tag + date
│   │   ├── NoteCards.vue       # v-if activeTab === 'text'
│   │   │   └── NoteCard.vue    # 2-column grid; card with title/excerpt/date
│   │   └── Pagination.vue      # Page navigation at bottom of list/cards
│   └── DetailPanel.vue         # v-if selectedItem; slides from right
│       ├── Back + Title + Edit/Save button + More actions
│       ├── Category tag + meta info
│       ├── Read mode: rendered content (marked for notes)
│       └── Edit mode: inline form (title + content + category) after clicking "Edit"
├── Toast.vue                   # Global toast notification (teleported to body)
└── ConfirmDialog.vue           # Global confirmation dialog (teleported to body)
```

### Pinia Store: `useNotesStore`
| State | Type | Description |
|-------|------|-------------|
| todos | ref([]) | Todo list |
| notes | ref([]) | Note list |
| categories | ref([]) | Available categories (fetched from /api/v1/categories) |
| activeTab | ref("todo") | Current view tab |
| activeCategory | ref("全部") | Selected category filter |
| searchQuery | ref("") | Search keyword |
| selectedItem | ref(null) | Current detail item (fetched via GET /:id) |
| selectedType | ref(null) | "todo" or "note" — determines DetailPanel rendering |
| isTodosLoading | ref(false) | Loading state for todo list |
| isNotesLoading | ref(false) | Loading state for note list |
| isDetailLoading | ref(false) | Loading state for detail fetch |
| error | ref(null) | Global error state |

### API Layer: `api/index.js`
Axios instance with `baseURL: '/api/v1'`. All functions return promises; callers handle try/catch.

```
fetchCategories()     → GET  /categories
fetchTodos(params)    → GET  /todos
createTodo(data)      → POST /todos
fetchTodo(id)         → GET  /todos/:id
updateTodo(id, data)  → PUT/PATCH /todos/:id
deleteTodo(id)        → DELETE /todos/:id

fetchNotes(params)    → GET  /notes
createNote(data)      → POST /notes
fetchNote(id)         → GET  /notes/:id
updateNote(id, data)  → PUT/PATCH /notes/:id
deleteNote(id)        → DELETE /notes/:id
```

### Data Flow (Frontend)
```
Sidebar (category) ──→ Pinia Store ←── ContentArea (tab/search)
DetailPanel ←── Pinia Store ←── api/axios ←── Django Response
              ↓                          ↑
              └──────────────────────────┘
                   HTTP request to /api/v1/*
```

---

## Interaction Flows

### Unified Update Strategy

| Operation | Update style | On Success | On Failure |
|-----------|-------------|-----------|------------|
| Create | Pessimistic | If no filter active: push to store head. If filter/search active: re-fetch list | Toast error, no store change |
| Update | Pessimistic | Replace store item with returned object | Toast error, rollback to old value |
| Delete | Pessimistic | Splice from store; if last item on page, go to previous page | Toast error, keep data |
| Toggle complete | **Optimistic** | Confirm state already set (no-op) | Rollback is_completed to old value + toast error |

Toggle complete uses optimistic update (immediate UI feedback, strikethrough). All other mutations use pessimistic (wait for API success, then update store).

### Flow 1: Load List
1. App mount / switch tab / click category
2. GET /todos or /notes with params: { category, q, page, page_size }
3. Loading: show skeleton while `isTodosLoading` or `isNotesLoading === true`
4. Success: update store array
5. Empty: show "暂无记录，点击 + 创建" placeholder
6. Error: show toast, keep previous data

### Flow 2: Create
1. Click + button → open editor in right panel (same slot as DetailPanel)
2. Fill title (required), content, select category
3. Validate before save: title non-empty, max 200 chars → block if invalid, show inline error
4. POST /todos or /notes
5. Success:
   - If no filter/search active: push returned object to store head → close editor
   - If filter/search active: re-fetch list (new item may not match current filter)
6. Error: toast "创建失败", editor stays open with data preserved

### Flow 3: View Detail
1. Click todo item / note card
2. Set `selectedId` + `selectedType` in store → open DetailPanel (show loading)
3. GET /todos/:id or /notes/:id
4. Success: store selectedItem → render in read mode (marked for Note, plain text for Todo)
5. Error: toast "加载失败", close panel

### Flow 4: Toggle Complete (Todo only)
1. Check/uncheck checkbox in TodoItem or DetailPanel
2. Optimistic: immediately toggle `is_completed` in store (strikethrough UI)
3. PATCH /todos/:id { is_completed: true/false }
4. Success: no further action (state already correct)
5. Error: rollback `is_completed` to previous value + toast "操作失败"

### Flow 5: Edit
1. Click "Edit" button in DetailPanel → switch panel from read mode to edit mode
2. Modify fields (title / content / category) in inline form
3. Validate: same rules as create
4. Click "Save" → PUT /todos/:id or /notes/:id (full update)
5. Success: replace item in store → switch panel back to read mode
6. Error: toast "保存失败", stay in edit mode with data preserved

### Flow 6: Delete
1. Click delete button in DetailPanel
2. Show ConfirmDialog: "确定删除这条记录？"
3. Confirm → DELETE /todos/:id or /notes/:id
4. Success: splice from store, close panel. If current page becomes empty after deletion, navigate to `max(1, page - 1)` and re-fetch.
5. Error: toast "删除失败", keep data
6. Cancel confirmation → no action

### Flow 7: Search
1. Type in search box
2. Debounce 300ms → set `searchQuery` in store
3. Watcher triggers: re-fetch list with `?q=keyword` + current category filter
4. If input cleared: reset to full list (no q param)

### Flow 8: Category Switch
1. Click category in sidebar
2. Debounce 150ms → set `activeCategory` in store
3. Watcher triggers: re-fetch list with `?category=xxx` + current search query
4. Rapid consecutive clicks: only last one fires request

### Flow 9: Cancel Edit
1. Click cancel in editor panel / modal
2. Close panel, discard all form data
3. No API call made

### Flow 10: Pagination
1. List loads with `?page=1&page_size=20` by default
2. Backend returns: `{ count: total, results: [...items] }`
3. Frontend pagination component at bottom of list
4. Page change triggers re-fetch with new page param
5. Category/type switch resets page to 1

### Flow 11: Loading State
- Todo list fetch: `isTodosLoading = true` → TodoList shows skeleton
- Note list fetch: `isNotesLoading = true` → NoteCards shows skeleton
- Detail fetch: `isDetailLoading = true` → DetailPanel shows spinner
- Switching tabs does not reset the other tab's data or loading state (both lists cached in store)
- On response (success or error), clear the corresponding loading flag

### Flow 12: Empty State
- When list returns 0 items and no error: show "暂无记录" with illustration
- Filtered empty: "当前分类下暂无记录"
- Search empty: "未找到匹配的记录"

---

## Visual Spec

| Property | Value |
|----------|-------|
| Primary | #4f6ef7 (blue) |
| Background | #f5f7fa (main), #ffffff (cards/panels) |
| Text | #1a1a1a (headings), #666666 (body), #999999 (aux) |
| Category tags | 工作=#3b82f6, 学习=#22c55e, 生活=#a855f7, 想法=#f59e0b |
| Border radius | 8px (cards/buttons), 12px (large containers) |
| Shadow | 0 2px 8px rgba(0,0,0,0.06) (cards), 0 4px 16px rgba(0,0,0,0.1) (modals) |
| Font | -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif |

---

## Out of Scope

- Authentication / login page (single-user mode)
- Google OAuth
- AI summary feature
- Batch operations (multi-select delete/complete)
- Deployment configuration (local dev only)

## .gitignore

Add `.superpowers/` to `.gitignore` — visual companion session files should not be committed.

## CSS Approach

Scoped CSS in Vue SFCs (`<style scoped>`). No external CSS framework. Visual spec values defined as CSS custom properties in `App.vue` for global reuse.

## Dependencies

### Backend (requirements.txt)
- Django ~4.2
- djangorestframework
- django-cors-headers

Filtering is done via custom `get_queryset` — `django-filter` is not needed.

### Frontend (package.json)
- vue ~3.4
- vue-router ~4
- pinia ~2
- axios
- marked (Markdown rendering)
- vite
- @vitejs/plugin-vue (Vite Vue3 SFC compiler)

Toast notifications and confirmation dialog are implemented as simple Vue components (Toast.vue, ConfirmDialog.vue) — no external UI library needed.

---

## Dev Workflow

1. Start Django: `cd backend && python manage.py runserver` (port 8000)
2. Start Vite: `cd frontend && npm run dev` (port 5173)
3. Vite proxies `/api/*` → `http://localhost:8000`
4. Open browser at `http://localhost:5173`

---

## Project Structure
```
web-notepad/
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── config/          # settings.py, urls.py, wsgi.py
│   └── notes/           # models.py, serializers.py, views.py, urls.py
├── frontend/
│   ├── package.json
│   ├── vite.config.js   # proxy /api → :8000
│   └── src/
│       ├── main.js
│       ├── App.vue
│       ├── router/index.js
│       ├── stores/notes.js
│       ├── views/MainLayout.vue
│       ├── components/  # Sidebar, ContentArea, TopBar, TodoList, NoteCards, DetailPanel, ...
│       └── api/index.js
└── README.md
```
