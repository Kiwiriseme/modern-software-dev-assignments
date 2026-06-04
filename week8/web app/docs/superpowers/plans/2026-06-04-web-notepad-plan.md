# 网页记事本 (Web Notepad) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a full-stack note-taking and todo management app with Vue3 frontend and Django REST backend.

**Architecture:** Django serves REST API at `/api/v1/*` with SQLite persistence. Vue3 SPA runs on Vite dev server (port 5173), proxying API requests to Django (port 8000). Single Pinia store manages all frontend state. No authentication.

**Tech Stack:** Vue 3.4, Vite, Pinia 2, Vue Router 4, Axios, marked, Django 4.2, Django REST Framework, django-cors-headers, SQLite

---

### Task 1: Scaffold Django project and app

**Files:**
- Create: `backend/config/settings.py`
- Create: `backend/config/urls.py`
- Create: `backend/config/wsgi.py`
- Create: `backend/manage.py`
- Create: `backend/notes/models.py`
- Create: `backend/notes/admin.py`
- Create: `backend/notes/apps.py`
- Create: `backend/requirements.txt`

- [ ] **Step 1: Install Django and create project structure**

Run: `cd "d:/project/cs146s/web app" && pip install django djangorestframework django-cors-headers`

Run: `cd "d:/project/cs146s/web app" && django-admin startproject config backend`

Run: `cd "d:/project/cs146s/web app/backend" && python manage.py startapp notes`

- [ ] **Step 2: Write requirements.txt**

Write to `backend/requirements.txt`:
```
Django>=4.2,<5.0
djangorestframework>=3.14,<4.0
django-cors-headers>=4.0,<5.0
```

- [ ] **Step 3: Configure settings.py**

Write `backend/config/settings.py`:
```python
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-dev-key-for-local-only'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'notes',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOW_ALL_ORIGINS = True

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'MAX_PAGE_SIZE': 100,
    'PAGE_SIZE_QUERY_PARAM': 'page_size',
}
```

- [ ] **Step 4: Configure root URLconf**

Write `backend/config/urls.py`:
```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('notes.urls')),
]
```

- [ ] **Step 5: Run initial migration and verify**

Run: `cd "d:/project/cs146s/web app/backend" && python manage.py migrate`

Expected: "Applying contenttypes... OK", "Applying auth... OK", etc. No errors.

- [ ] **Step 6: Verify server starts**

Run: `cd "d:/project/cs146s/web app/backend" && python manage.py runserver 8000` and check it does not crash. Stop with Ctrl+C after confirming.

---

### Task 2: Define Todo and Note models

**Files:**
- Modify: `backend/notes/models.py`
- Create (migration): auto-generated

- [ ] **Step 1: Write the models**

Write `backend/notes/models.py`:
```python
from django.db import models


class Todo(models.Model):
    CATEGORY_CHOICES = [
        ('工作', '工作'),
        ('学习', '学习'),
        ('生活', '生活'),
        ('想法', '想法'),
    ]

    title = models.CharField(max_length=200)
    content = models.TextField(blank=True, default='')
    category = models.CharField(max_length=50, blank=True, default='')
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Note(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True, default='')
    category = models.CharField(max_length=50, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
```

- [ ] **Step 2: Make and run migrations**

Run: `cd "d:/project/cs146s/web app/backend" && python manage.py makemigrations notes`

Expected: "Create model Todo" and "Create model Note"

Run: `cd "d:/project/cs146s/web app/backend" && python manage.py migrate`

Expected: "Applying notes.0001_initial... OK"

- [ ] **Step 3: Run model tests**

Write `backend/notes/tests.py`:
```python
from django.test import TestCase
from django.core.exceptions import ValidationError
from notes.models import Todo, Note


class TodoModelTest(TestCase):
    def test_create_todo_with_minimal_fields(self):
        todo = Todo.objects.create(title='Buy groceries')
        self.assertEqual(todo.title, 'Buy groceries')
        self.assertEqual(todo.content, '')
        self.assertEqual(todo.category, '')
        self.assertFalse(todo.is_completed)
        self.assertIsNotNone(todo.created_at)
        self.assertIsNotNone(todo.updated_at)

    def test_create_todo_with_all_fields(self):
        todo = Todo.objects.create(
            title='Finish report',
            content='Need to include charts',
            category='工作',
            is_completed=True,
        )
        self.assertEqual(todo.content, 'Need to include charts')
        self.assertEqual(todo.category, '工作')
        self.assertTrue(todo.is_completed)

    def test_todo_ordering(self):
        t1 = Todo.objects.create(title='First', category='工作')
        t2 = Todo.objects.create(title='Second', category='工作')
        todos = list(Todo.objects.all())
        self.assertEqual(todos[0].title, 'Second')
        self.assertEqual(todos[1].title, 'First')

    def test_title_max_length(self):
        Todo.objects.create(title='a' * 200)
        with self.assertRaises(Exception):
            Todo.objects.create(title='a' * 201)


class NoteModelTest(TestCase):
    def test_create_note(self):
        note = Note.objects.create(
            title='Meeting Notes',
            content='## Agenda\n- Item 1\n- Item 2',
            category='工作',
        )
        self.assertEqual(note.title, 'Meeting Notes')
        self.assertEqual(note.category, '工作')
        self.assertFalse(note.content == '')

    def test_note_defaults(self):
        note = Note.objects.create(title='Quick Note')
        self.assertEqual(note.content, '')
        self.assertEqual(note.category, '')
```

Run: `cd "d:/project/cs146s/web app/backend" && python manage.py test notes`

Expected: 6 tests pass.

---

### Task 3: Write serializers

**Files:**
- Create: `backend/notes/serializers.py`
- Modify: `backend/notes/tests.py` (append serializer tests)

- [ ] **Step 1: Write serializers**

Write `backend/notes/serializers.py`:
```python
from rest_framework import serializers
from notes.models import Todo, Note


class TodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Todo
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_title(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('标题不能为空')
        if len(value) > 200:
            raise serializers.ValidationError('标题不能超过200个字符')
        return value.strip()

    def validate_category(self, value):
        if value:
            value = value.strip()
        if len(value) > 50:
            raise serializers.ValidationError('分类名称不能超过50个字符')
        return value

    def validate_content(self, value):
        if len(value) > 10000:
            raise serializers.ValidationError('内容不能超过10000个字符')
        return value


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_title(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('标题不能为空')
        if len(value) > 200:
            raise serializers.ValidationError('标题不能超过200个字符')
        return value.strip()

    def validate_category(self, value):
        if value:
            value = value.strip()
        if len(value) > 50:
            raise serializers.ValidationError('分类名称不能超过50个字符')
        return value

    def validate_content(self, value):
        if len(value) > 10000:
            raise serializers.ValidationError('内容不能超过10000个字符')
        return value
```

- [ ] **Step 2: Write serializer tests**

Append to `backend/notes/tests.py`:
```python
from notes.serializers import TodoSerializer, NoteSerializer


class TodoSerializerTest(TestCase):
    def test_valid_todo(self):
        data = {'title': 'Test Todo', 'category': '工作'}
        serializer = TodoSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_empty_title_rejected(self):
        data = {'title': '', 'category': '工作'}
        serializer = TodoSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('title', serializer.errors)

    def test_whitespace_only_title_rejected(self):
        data = {'title': '   ', 'category': '工作'}
        serializer = TodoSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_title_stripped_on_validation(self):
        data = {'title': '  Clean me  ', 'category': '工作'}
        serializer = TodoSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['title'], 'Clean me')

    def test_category_stripped(self):
        data = {'title': 'Test', 'category': ' 工作 '}
        serializer = TodoSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['category'], '工作')

    def test_content_max_length(self):
        data = {'title': 'Test', 'content': 'a' * 10001}
        serializer = TodoSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('content', serializer.errors)

    def test_category_max_length(self):
        data = {'title': 'Test', 'category': 'a' * 51}
        serializer = TodoSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('category', serializer.errors)


class NoteSerializerTest(TestCase):
    def test_valid_note(self):
        data = {'title': 'Meeting Notes', 'content': '# Agenda', 'category': '工作'}
        serializer = NoteSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_empty_title_rejected(self):
        data = {'title': '', 'content': 'Some content'}
        serializer = NoteSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('title', serializer.errors)
```

Run: `cd "d:/project/cs146s/web app/backend" && python manage.py test notes`

Expected: 14 tests pass (6 model + 8 serializer).

---

### Task 4: Write Todo API views and URL routing

**Files:**
- Create: `backend/notes/views.py`
- Create: `backend/notes/urls.py`
- Modify: `backend/notes/tests.py` (append API tests)

- [ ] **Step 1: Write TodoViewSet and NoteViewSet**

Write `backend/notes/views.py`:
```python
from django.db import models
from rest_framework import viewsets
from notes.models import Todo, Note
from notes.serializers import TodoSerializer, NoteSerializer


class TodoViewSet(viewsets.ModelViewSet):
    serializer_class = TodoSerializer

    def get_queryset(self):
        queryset = Todo.objects.all()
        category = self.request.query_params.get('category', None)
        q = self.request.query_params.get('q', None)
        if category and category != '全部':
            queryset = queryset.filter(category=category)
        if q:
            queryset = queryset.filter(
                models.Q(title__icontains=q) | models.Q(content__icontains=q)
            )
        return queryset


class NoteViewSet(viewsets.ModelViewSet):
    serializer_class = NoteSerializer

    def get_queryset(self):
        queryset = Note.objects.all()
        category = self.request.query_params.get('category', None)
        q = self.request.query_params.get('q', None)
        if category and category != '全部':
            queryset = queryset.filter(category=category)
        if q:
            queryset = queryset.filter(
                models.Q(title__icontains=q) | models.Q(content__icontains=q)
            )
        return queryset
```

- [ ] **Step 2: Write URL routing**

Write `backend/notes/urls.py`:
```python
from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework.views import APIView
from rest_framework.response import Response
from notes.views import TodoViewSet, NoteViewSet
from notes.models import Todo, Note

router = DefaultRouter(trailing_slash=False)
router.register(r'todos', TodoViewSet, basename='todo')
router.register(r'notes', NoteViewSet, basename='note')


class CategoryListView(APIView):
    def get(self, request):
        todo_categories = Todo.objects.exclude(
            category=''
        ).values_list('category', flat=True).distinct()
        note_categories = Note.objects.exclude(
            category=''
        ).values_list('category', flat=True).distinct()
        all_categories = sorted(set(
            list(todo_categories) + list(note_categories)
        ))
        return Response(all_categories)


urlpatterns = router.urls + [
    path('categories', CategoryListView.as_view(), name='categories'),
]
```

- [ ] **Step 3: Write API integration tests**

Append to `backend/notes/tests.py`:
```python
from rest_framework.test import APITestCase
from rest_framework import status


class TodoAPITest(APITestCase):
    def setUp(self):
        self.todo = Todo.objects.create(title='Test Todo', category='工作')

    def test_list_todos(self):
        response = self.client.get('/api/v1/todos')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_create_todo(self):
        response = self.client.post('/api/v1/todos', {
            'title': 'New Todo',
            'category': '学习',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Todo.objects.count(), 2)

    def test_get_todo_detail(self):
        response = self.client.get(f'/api/v1/todos/{self.todo.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Todo')

    def test_update_todo(self):
        response = self.client.put(f'/api/v1/todos/{self.todo.id}', {
            'title': 'Updated Todo',
            'category': '生活',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.todo.refresh_from_db()
        self.assertEqual(self.todo.title, 'Updated Todo')
        self.assertEqual(self.todo.category, '生活')

    def test_patch_toggle_complete(self):
        response = self.client.patch(f'/api/v1/todos/{self.todo.id}', {
            'is_completed': True,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.todo.refresh_from_db()
        self.assertTrue(self.todo.is_completed)

    def test_delete_todo(self):
        response = self.client.delete(f'/api/v1/todos/{self.todo.id}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Todo.objects.count(), 0)

    def test_filter_by_category(self):
        Todo.objects.create(title='Study', category='学习')
        response = self.client.get('/api/v1/todos?category=学习')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_search_todos(self):
        Todo.objects.create(title='Buy milk', content='Grocery shopping')
        response = self.client.get('/api/v1/todos?q=milk')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_create_invalid_todo(self):
        response = self.client.post('/api/v1/todos', {
            'title': '',
            'category': '工作',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_pagination(self):
        for i in range(25):
            Todo.objects.create(title=f'Todo {i}', category='工作')
        response = self.client.get('/api/v1/todos?page_size=10')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)
        self.assertEqual(response.data['count'], 26)


class NoteAPITest(APITestCase):
    def setUp(self):
        self.note = Note.objects.create(title='Meeting Notes', content='## Agenda', category='工作')

    def test_list_notes(self):
        response = self.client.get('/api/v1/notes')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_create_note(self):
        response = self.client.post('/api/v1/notes', {
            'title': 'Ideas',
            'content': 'Some ideas here',
            'category': '想法',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Note.objects.count(), 2)

    def test_get_note_detail(self):
        response = self.client.get(f'/api/v1/notes/{self.note.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Meeting Notes')

    def test_update_note(self):
        response = self.client.put(f'/api/v1/notes/{self.note.id}', {
            'title': 'Updated Notes',
            'content': 'Updated content',
            'category': '学习',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, 'Updated Notes')

    def test_delete_note(self):
        response = self.client.delete(f'/api/v1/notes/{self.note.id}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class CategoryAPITest(APITestCase):
    def test_get_categories(self):
        Todo.objects.create(title='T1', category='工作')
        Todo.objects.create(title='T2', category='学习')
        Note.objects.create(title='N1', category='生活')
        response = self.client.get('/api/v1/categories')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(sorted(response.data), ['工作', '学习', '生活'])

    def test_categories_deduplicated(self):
        Todo.objects.create(title='T1', category='工作')
        Note.objects.create(title='N1', category='工作')
        response = self.client.get('/api/v1/categories')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, ['工作'])

    def test_empty_category_excluded(self):
        Todo.objects.create(title='T1', category='')
        response = self.client.get('/api/v1/categories')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])
```

Run: `cd "d:/project/cs146s/web app/backend" && python manage.py test notes`

Expected: 30 tests pass (6 model + 8 serializer + 10 todo api + 5 note api + 3 category).

---

### Task 5: Scaffold Vue3 + Vite frontend

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.js`
- Create: `frontend/index.html`
- Create: `frontend/src/main.js`
- Create: `frontend/src/App.vue`

- [ ] **Step 1: Create package.json**

Write `frontend/package.json`:
```json
{
  "name": "web-notepad",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.3.0",
    "pinia": "^2.1.0",
    "axios": "^1.7.0",
    "marked": "^12.0.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "vite": "^5.4.0"
  }
}
```

- [ ] **Step 2: Install dependencies**

Run: `cd "d:/project/cs146s/web app/frontend" && npm install`

- [ ] **Step 3: Create vite.config.js**

Write `frontend/vite.config.js`:
```js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

- [ ] **Step 4: Create index.html**

Write `frontend/index.html`:
```html
<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>网页记事本</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.js"></script>
  </body>
</html>
```

- [ ] **Step 5: Create main.js**

Write `frontend/src/main.js`:
```js
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router/index.js'
import App from './App.vue'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
```

- [ ] **Step 6: Create minimal App.vue**

Write `frontend/src/App.vue`:
```html
<template>
  <router-view />
</template>
```

- [ ] **Step 7: Create router stub**

Write `frontend/src/router/index.js`:
```js
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('../../views/MainLayout.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
```

- [ ] **Step 8: Create placeholder MainLayout.vue**

Write `frontend/src/views/MainLayout.vue`:
```html
<template>
  <div>MainLayout placeholder — Vue app is running</div>
</template>
```

- [ ] **Step 9: Verify Vite dev server starts**

Run: `cd "d:/project/cs146s/web app/frontend" && npm run dev`

Expected: "VITE v5.x.x ready in xxx ms" → "Local: http://localhost:5173/"

Open http://localhost:5173 in browser. Should show "MainLayout placeholder — Vue app is running". Stop with Ctrl+C.

---

### Task 6: Create Pinia store

**Files:**
- Create: `frontend/src/stores/notes.js`

- [ ] **Step 1: Write the store**

Write `frontend/src/stores/notes.js`:
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
  deleteTodo,
  deleteNote,
} from '../api/index.js'

export const useNotesStore = defineStore('notes', () => {
  const todos = ref([])
  const notes = ref([])
  const categories = ref([])
  const activeTab = ref('todo')
  const activeCategory = ref('全部')
  const searchQuery = ref('')
  const selectedItem = ref(null)
  const selectedType = ref(null)
  const isTodosLoading = ref(false)
  const isNotesLoading = ref(false)
  const isDetailLoading = ref(false)
  const error = ref(null)

  const currentPage = ref(1)
  const totalCount = ref(0)
  const pageSize = 20

  function getListParams() {
    const params = { page: currentPage.value, page_size: pageSize }
    if (activeCategory.value !== '全部') {
      params.category = activeCategory.value
    }
    if (searchQuery.value) {
      params.q = searchQuery.value
    }
    return params
  }

  async function loadTodos() {
    isTodosLoading.value = true
    error.value = null
    try {
      const params = getListParams()
      const res = await fetchTodos(params)
      todos.value = res.data.results
      totalCount.value = res.data.count
    } catch (e) {
      error.value = e.response?.data?.detail || e.message || '加载待办失败'
      throw e
    } finally {
      isTodosLoading.value = false
    }
  }

  async function loadNotes() {
    isNotesLoading.value = true
    error.value = null
    try {
      const params = getListParams()
      const res = await fetchNotes(params)
      notes.value = res.data.results
      totalCount.value = res.data.count
    } catch (e) {
      error.value = e.response?.data?.detail || e.message || '加载笔记失败'
      throw e
    } finally {
      isNotesLoading.value = false
    }
  }

  async function loadCategories() {
    try {
      const res = await fetchCategories()
      categories.value = res.data
    } catch (e) {
      // categories load failure is non-critical, just log
      console.error('Failed to load categories', e)
    }
  }

  async function addTodo(data) {
    const res = await createTodo(data)
    const hasFilter = activeCategory.value !== '全部' || searchQuery.value !== ''
    if (hasFilter) {
      await loadTodos()
    } else {
      todos.value.unshift(res.data)
      totalCount.value++
    }
    return res.data
  }

  async function addNote(data) {
    const res = await createNote(data)
    const hasFilter = activeCategory.value !== '全部' || searchQuery.value !== ''
    if (hasFilter) {
      await loadNotes()
    } else {
      notes.value.unshift(res.data)
      totalCount.value++
    }
    return res.data
  }

  async function openDetail(id, type) {
    selectedType.value = type
    selectedItem.value = null
    isDetailLoading.value = true
    try {
      const fn = type === 'todo' ? fetchTodo : fetchNote
      const res = await fn(id)
      selectedItem.value = res.data
    } catch (e) {
      selectedType.value = null
      throw e
    } finally {
      isDetailLoading.value = false
    }
  }

  function closeDetail() {
    selectedItem.value = null
    selectedType.value = null
  }

  async function toggleTodoComplete(todo) {
    const previousValue = todo.is_completed
    todo.is_completed = !todo.is_completed
    try {
      await updateTodo(todo.id, { is_completed: todo.is_completed })
    } catch (e) {
      todo.is_completed = previousValue
      throw e
    }
  }

  async function saveTodoEdit(id, data) {
    const oldItem = todos.value.find(t => t.id === id)
    const oldData = oldItem ? { ...oldItem } : null
    try {
      const res = await updateTodo(id, data)
      if (oldItem) {
        Object.assign(oldItem, res.data)
      }
      if (selectedItem.value && selectedItem.value.id === id) {
        selectedItem.value = res.data
      }
      return res.data
    } catch (e) {
      if (oldItem && oldData) {
        Object.assign(oldItem, oldData)
      }
      throw e
    }
  }

  async function saveNoteEdit(id, data) {
    const oldItem = notes.value.find(n => n.id === id)
    const oldData = oldItem ? { ...oldItem } : null
    try {
      const res = await updateNote(id, data)
      if (oldItem) {
        Object.assign(oldItem, res.data)
      }
      if (selectedItem.value && selectedItem.value.id === id) {
        selectedItem.value = res.data
      }
      return res.data
    } catch (e) {
      if (oldItem && oldData) {
        Object.assign(oldItem, oldData)
      }
      throw e
    }
  }

  async function removeTodo(id) {
    await deleteTodo(id)
    const idx = todos.value.findIndex(t => t.id === id)
    if (idx !== -1) {
      todos.value.splice(idx, 1)
      totalCount.value--
    }
    if (todos.value.length === 0 && currentPage.value > 1) {
      currentPage.value = Math.max(1, currentPage.value - 1)
      await loadTodos()
    }
  }

  async function removeNote(id) {
    await deleteNote(id)
    const idx = notes.value.findIndex(n => n.id === id)
    if (idx !== -1) {
      notes.value.splice(idx, 1)
      totalCount.value--
    }
    if (notes.value.length === 0 && currentPage.value > 1) {
      currentPage.value = Math.max(1, currentPage.value - 1)
      await loadNotes()
    }
  }

  function setActiveTab(tab) {
    activeTab.value = tab
    currentPage.value = 1
  }

  function setActiveCategory(category) {
    activeCategory.value = category
    currentPage.value = 1
  }

  function setSearchQuery(query) {
    searchQuery.value = query
    currentPage.value = 1
  }

  function setPage(page) {
    currentPage.value = page
  }

  return {
    todos, notes, categories,
    activeTab, activeCategory, searchQuery,
    selectedItem, selectedType,
    isTodosLoading, isNotesLoading, isDetailLoading,
    error, currentPage, totalCount, pageSize,
    loadTodos, loadNotes, loadCategories,
    addTodo, addNote,
    openDetail, closeDetail,
    toggleTodoComplete,
    saveTodoEdit, saveNoteEdit,
    removeTodo, removeNote,
    setActiveTab, setActiveCategory, setSearchQuery, setPage,
  }
})
```

---

### Task 7: Create API layer

**Files:**
- Create: `frontend/src/api/index.js`

- [ ] **Step 1: Write API functions**

Write `frontend/src/api/index.js`:
```js
import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
})

export function fetchCategories() {
  return api.get('/categories')
}

export function fetchTodos(params = {}) {
  return api.get('/todos', { params })
}

export function createTodo(data) {
  return api.post('/todos', data)
}

export function fetchTodo(id) {
  return api.get(`/todos/${id}`)
}

export function updateTodo(id, data) {
  return api.put(`/todos/${id}`, data)
}

export function deleteTodo(id) {
  return api.delete(`/todos/${id}`)
}

export function fetchNotes(params = {}) {
  return api.get('/notes', { params })
}

export function createNote(data) {
  return api.post('/notes', data)
}

export function fetchNote(id) {
  return api.get(`/notes/${id}`)
}

export function updateNote(id, data) {
  return api.put(`/notes/${id}`, data)
}

export function deleteNote(id) {
  return api.delete(`/notes/${id}`)
}

export default api
```

---

### Task 8: Build Toast and ConfirmDialog components

**Files:**
- Create: `frontend/src/components/Toast.vue`
- Create: `frontend/src/components/ConfirmDialog.vue`

- [ ] **Step 1: Write Toast.vue**

Write `frontend/src/components/Toast.vue`:
```html
<template>
  <Teleport to="body">
    <Transition name="toast">
      <div v-if="visible" class="toast" :class="type">
        {{ message }}
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  message: { type: String, default: '' },
  type: { type: String, default: 'error' },
  duration: { type: Number, default: 3000 },
  trigger: { type: Number, default: 0 },
})

const visible = ref(false)
let timer = null

watch(() => props.trigger, () => {
  if (props.trigger > 0) {
    visible.value = true
    clearTimeout(timer)
    timer = setTimeout(() => {
      visible.value = false
    }, props.duration)
  }
})
</script>

<style scoped>
.toast {
  position: fixed;
  top: 24px;
  left: 50%;
  transform: translateX(-50%);
  padding: 10px 24px;
  border-radius: 8px;
  font-size: 14px;
  z-index: 9999;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  white-space: nowrap;
}
.toast.error {
  background: #fef2f2;
  color: #dc2626;
  border: 1px solid #fecaca;
}
.toast.success {
  background: #f0fdf4;
  color: #16a34a;
  border: 1px solid #bbf7d0;
}
.toast-enter-active, .toast-leave-active {
  transition: all 0.3s ease;
}
.toast-enter-from, .toast-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-12px);
}
</style>
```

- [ ] **Step 2: Write ConfirmDialog.vue**

Write `frontend/src/components/ConfirmDialog.vue`:
```html
<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="visible" class="overlay" @click.self="$emit('cancel')">
        <div class="dialog">
          <p class="dialog-message">{{ message }}</p>
          <div class="dialog-actions">
            <button class="btn-cancel" @click="$emit('cancel')">取消</button>
            <button class="btn-confirm" @click="$emit('confirm')">确定</button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
defineProps({
  visible: { type: Boolean, default: false },
  message: { type: String, default: '确定执行此操作？' },
})

defineEmits(['confirm', 'cancel'])
</script>

<style scoped>
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
}
.dialog {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  min-width: 320px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}
.dialog-message {
  font-size: 15px;
  color: #1a1a1a;
  margin: 0 0 20px 0;
  text-align: center;
}
.dialog-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}
.btn-cancel {
  padding: 8px 24px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: #fff;
  color: #666;
  cursor: pointer;
  font-size: 14px;
}
.btn-confirm {
  padding: 8px 24px;
  border: none;
  border-radius: 8px;
  background: #4f6ef7;
  color: #fff;
  cursor: pointer;
  font-size: 14px;
}
.btn-confirm:hover {
  background: #3d5bd9;
}
.modal-enter-active, .modal-leave-active {
  transition: opacity 0.2s ease;
}
.modal-enter-from, .modal-leave-to {
  opacity: 0;
}
</style>
```

---

### Task 9: Build Sidebar component

**Files:**
- Create: `frontend/src/components/Sidebar.vue`

- [ ] **Step 1: Write Sidebar.vue**

Write `frontend/src/components/Sidebar.vue`:
```html
<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <div class="avatar">📓</div>
      <div class="brand">网页记事本</div>
    </div>
    <nav class="nav-list">
      <button
        v-for="cat in displayCategories"
        :key="cat"
        class="nav-item"
        :class="{ active: store.activeCategory === cat }"
        @click="store.setActiveCategory(cat)"
      >
        {{ cat }}
      </button>
    </nav>
    <div class="sidebar-footer">
      <span class="settings-icon">⚙</span>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { useNotesStore } from '../stores/notes.js'

const store = useNotesStore()

const presetCategories = ['全部', '工作', '学习', '生活', '想法']

const displayCategories = computed(() => {
  const custom = store.categories.filter(c => !presetCategories.includes(c))
  return [...presetCategories, ...custom]
})
</script>

<style scoped>
.sidebar {
  width: 200px;
  min-width: 200px;
  background: #fafbfc;
  border-right: 1px solid #eee;
  display: flex;
  flex-direction: column;
  height: 100vh;
}
.sidebar-header {
  padding: 20px 16px;
  display: flex;
  align-items: center;
  gap: 10px;
}
.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #4f6ef7;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  color: #fff;
  flex-shrink: 0;
}
.brand {
  font-weight: 700;
  font-size: 14px;
  color: #1a1a1a;
}
.nav-list {
  flex: 1;
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 2px;
  overflow-y: auto;
}
.nav-item {
  display: block;
  width: 100%;
  padding: 10px 12px;
  border: none;
  border-radius: 8px;
  background: transparent;
  text-align: left;
  font-size: 14px;
  color: #333;
  cursor: pointer;
  transition: background 0.15s;
}
.nav-item:hover {
  background: #f0f4ff;
}
.nav-item.active {
  background: #e8f0fe;
  color: #4f6ef7;
  font-weight: 600;
}
.sidebar-footer {
  padding: 12px 16px;
  border-top: 1px solid #eee;
}
.settings-icon {
  font-size: 18px;
  color: #999;
  cursor: pointer;
}
</style>
```

---

### Task 10: Build TopBar component

**Files:**
- Create: `frontend/src/components/TopBar.vue`

- [ ] **Step 1: Write TopBar.vue**

Write `frontend/src/components/TopBar.vue`:
```html
<template>
  <div class="topbar">
    <input
      class="search-input"
      :placeholder="store.activeTab === 'todo' ? '搜索 TODO...' : '搜索文本...'"
      :value="localSearch"
      @input="onSearchInput"
    />
    <div class="tab-switch">
      <button
        class="tab-btn"
        :class="{ active: store.activeTab === 'todo' }"
        @click="store.setActiveTab('todo')"
      >TODO</button>
      <button
        class="tab-btn"
        :class="{ active: store.activeTab === 'text' }"
        @click="store.setActiveTab('text')"
      >文本</button>
    </div>
    <button class="new-btn" @click="startCreate">＋</button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useNotesStore } from '../stores/notes.js'

const emit = defineEmits(['create'])
const store = useNotesStore()
const localSearch = ref('')
let debounceTimer = null

function onSearchInput(e) {
  localSearch.value = e.target.value
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    store.setSearchQuery(localSearch.value)
    if (store.activeTab === 'todo') {
      store.loadTodos()
    } else {
      store.loadNotes()
    }
  }, 300)
}

function startCreate() {
  emit('create')
}
</script>

<style scoped>
.topbar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
}
.search-input {
  flex: 1;
  padding: 8px 14px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 13px;
  outline: none;
  background: #fff;
  color: #333;
}
.search-input::placeholder {
  color: #999;
}
.search-input:focus {
  border-color: #4f6ef7;
}
.tab-switch {
  display: flex;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e0e0e0;
  flex-shrink: 0;
}
.tab-btn {
  padding: 7px 16px;
  border: none;
  background: #fff;
  font-size: 13px;
  color: #666;
  cursor: pointer;
  transition: all 0.15s;
}
.tab-btn:first-child {
  border-right: 1px solid #e0e0e0;
}
.tab-btn.active {
  background: #4f6ef7;
  color: #fff;
}
.new-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: none;
  background: #4f6ef7;
  color: #fff;
  font-size: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: background 0.15s;
}
.new-btn:hover {
  background: #3d5bd9;
}
</style>
```

---

### Task 11: Build TodoList and TodoItem components

**Files:**
- Create: `frontend/src/components/TodoList.vue`
- Create: `frontend/src/components/TodoItem.vue`

- [ ] **Step 1: Write TodoItem.vue**

Write `frontend/src/components/TodoItem.vue`:
```html
<template>
  <div
    class="todo-item"
    :class="{ completed: todo.is_completed }"
    @click="emit('select', todo)"
  >
    <input
      type="checkbox"
      class="checkbox"
      :checked="todo.is_completed"
      @click.stop
      @change="onToggle"
    />
    <span class="title">{{ todo.title }}</span>
    <span
      v-if="todo.category"
      class="category-tag"
      :style="{ background: categoryColor(todo.category) }"
    >{{ todo.category }}</span>
    <span class="date">{{ formatDate(todo.created_at) }}</span>
  </div>
</template>

<script setup>
import { useNotesStore } from '../stores/notes.js'

const props = defineProps({
  todo: { type: Object, required: true },
})

const emit = defineEmits(['select'])
const store = useNotesStore()

const categoryColors = {
  '工作': '#3b82f6',
  '学习': '#22c55e',
  '生活': '#a855f7',
  '想法': '#f59e0b',
}
const defaultColor = '#6b7280'

function categoryColor(cat) {
  return categoryColors[cat] || defaultColor
}

async function onToggle() {
  try {
    await store.toggleTodoComplete(props.todo)
  } catch (e) {
    // Toast notification handled by parent
  }
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const now = new Date()
  const diff = date.getTime() - new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime()
  const days = Math.round(diff / (1000 * 60 * 60 * 24))
  if (days === 0) return '今天'
  if (days === 1) return '明天'
  if (days === -1) return '昨天'
  return date.toISOString().split('T')[0]
}
</script>

<style scoped>
.todo-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  cursor: pointer;
  transition: background 0.1s;
}
.todo-item:hover {
  background: #f8f9fb;
}
.todo-item + .todo-item {
  border-top: 1px solid #f0f0f0;
}
.completed .title {
  text-decoration: line-through;
  color: #bbb;
}
.checkbox {
  width: 16px;
  height: 16px;
  cursor: pointer;
  accent-color: #4f6ef7;
  flex-shrink: 0;
}
.title {
  flex: 1;
  font-size: 14px;
  color: #1a1a1a;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.completed .title {
  color: #bbb;
}
.category-tag {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  color: #fff;
  flex-shrink: 0;
}
.date {
  font-size: 11px;
  color: #999;
  flex-shrink: 0;
}
</style>
```

- [ ] **Step 2: Write TodoList.vue**

Write `frontend/src/components/TodoList.vue`:
```html
<template>
  <div class="todo-list-container">
    <div v-if="store.isTodosLoading" class="loading">加载中...</div>
    <div v-else-if="store.todos.length === 0" class="empty">
      <p>{{ emptyMessage }}</p>
    </div>
    <div v-else class="todo-list">
      <TodoItem
        v-for="todo in store.todos"
        :key="todo.id"
        :todo="todo"
        @select="emit('select', todo, 'todo')"
      />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useNotesStore } from '../stores/notes.js'
import TodoItem from './TodoItem.vue'

const emit = defineEmits(['select'])
const store = useNotesStore()

const emptyMessage = computed(() => {
  if (store.searchQuery) return '未找到匹配的记录'
  if (store.activeCategory !== '全部') return '当前分类下暂无记录'
  return '暂无记录，点击 + 创建'
})
</script>

<style scoped>
.todo-list-container {
  flex: 1;
  overflow-y: auto;
}
.todo-list {
  background: #fff;
  border-radius: 8px;
}
.loading, .empty {
  padding: 40px;
  text-align: center;
  color: #999;
  font-size: 14px;
}
</style>
```

---

### Task 12: Build NoteCards and NoteCard components

**Files:**
- Create: `frontend/src/components/NoteCards.vue`
- Create: `frontend/src/components/NoteCard.vue`

- [ ] **Step 1: Write NoteCard.vue**

Write `frontend/src/components/NoteCard.vue`:
```html
<template>
  <div class="note-card" @click="emit('select', note, 'note')">
    <h3 class="card-title">{{ note.title }}</h3>
    <div class="card-meta">
      <span
        v-if="note.category"
        class="category-tag"
        :style="{ background: categoryColor(note.category) }"
      >{{ note.category }}</span>
    </div>
    <p class="card-excerpt">{{ excerpt }}</p>
    <span class="card-date">{{ formatDate(note.created_at) }}</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  note: { type: Object, required: true },
})

const emit = defineEmits(['select'])

const categoryColors = {
  '工作': '#3b82f6',
  '学习': '#22c55e',
  '生活': '#a855f7',
  '想法': '#f59e0b',
}
const defaultColor = '#6b7280'

function categoryColor(cat) {
  return categoryColors[cat] || defaultColor
}

const excerpt = computed(() => {
  const text = props.note.content || ''
  return text.length > 100 ? text.slice(0, 100) + '...' : text
})

function formatDate(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toISOString().split('T')[0]
}
</script>

<style scoped>
.note-card {
  background: #fff;
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.note-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}
.card-title {
  font-size: 15px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0;
}
.card-meta {
  display: flex;
  gap: 6px;
}
.category-tag {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  color: #fff;
}
.card-excerpt {
  font-size: 12px;
  color: #999;
  margin: 0;
  line-height: 1.4;
  flex: 1;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.card-date {
  font-size: 11px;
  color: #999;
  align-self: flex-end;
}
</style>
```

- [ ] **Step 2: Write NoteCards.vue**

Write `frontend/src/components/NoteCards.vue`:
```html
<template>
  <div class="note-cards-container">
    <div v-if="store.isNotesLoading" class="loading">加载中...</div>
    <div v-else-if="store.notes.length === 0" class="empty">
      <p>{{ emptyMessage }}</p>
    </div>
    <div v-else class="note-cards-grid">
      <NoteCard
        v-for="note in store.notes"
        :key="note.id"
        :note="note"
        @select="emit('select', note, 'note')"
      />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useNotesStore } from '../stores/notes.js'
import NoteCard from './NoteCard.vue'

const emit = defineEmits(['select'])
const store = useNotesStore()

const emptyMessage = computed(() => {
  if (store.searchQuery) return '未找到匹配的记录'
  if (store.activeCategory !== '全部') return '当前分类下暂无记录'
  return '暂无记录，点击 + 创建'
})
</script>

<style scoped>
.note-cards-container {
  flex: 1;
  overflow-y: auto;
  padding: 0 12px;
}
.note-cards-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}
.loading, .empty {
  padding: 40px;
  text-align: center;
  color: #999;
  font-size: 14px;
}
</style>
```

---

### Task 13: Build DetailPanel component

**Files:**
- Create: `frontend/src/components/DetailPanel.vue`

- [ ] **Step 1: Write DetailPanel.vue**

Write `frontend/src/components/DetailPanel.vue`:
```html
<template>
  <aside class="detail-panel" :class="{ open: store.selectedItem }">
    <template v-if="store.selectedItem">
      <div class="panel-header">
        <button class="back-btn" @click="store.closeDetail()">←</button>
        <span class="panel-title" v-if="!isEditing">{{ store.selectedItem.title }}</span>
        <div class="header-actions">
          <button
            v-if="!isEditing"
            class="action-btn edit-btn"
            @click="startEdit"
          >编辑</button>
          <button
            v-if="isEditing"
            class="action-btn save-btn"
            @click="save"
          >保存</button>
          <button
            v-if="isEditing"
            class="action-btn cancel-btn"
            @click="cancelEdit"
          >取消</button>
          <button
            v-if="!isEditing"
            class="action-btn delete-btn"
            @click="requestDelete"
          >删除</button>
        </div>
      </div>

      <div v-if="store.isDetailLoading" class="loading">加载中...</div>

      <template v-else>
        <div v-if="!isEditing" class="panel-body read-mode">
          <div class="meta-row">
            <span
              v-if="store.selectedItem.category"
              class="category-tag"
              :style="{ background: categoryColor(store.selectedItem.category) }"
            >
              {{ store.selectedItem.category }}
            </span>
            <span class="date-info">
              创建于 {{ formatDate(store.selectedItem.created_at) }}
            </span>
          </div>
          <div
            v-if="store.selectedType === 'note'"
            class="markdown-content"
            v-html="renderedMarkdown"
          ></div>
          <div v-else class="todo-detail-content">
            <p>{{ store.selectedItem.content || '暂无详细描述' }}</p>
            <div class="completion-status">
              <label>
                <input
                  type="checkbox"
                  :checked="store.selectedItem.is_completed"
                  @change="onToggleComplete"
                />
                {{ store.selectedItem.is_completed ? '已完成' : '未完成' }}
              </label>
            </div>
          </div>
        </div>

        <div v-else class="panel-body edit-mode">
          <div class="form-group">
            <label class="form-label">标题</label>
            <input
              v-model="editForm.title"
              class="form-input"
              :class="{ error: formErrors.title }"
              maxlength="200"
            />
            <span v-if="formErrors.title" class="form-error">{{ formErrors.title }}</span>
          </div>
          <div class="form-group">
            <label class="form-label">分类</label>
            <input
              v-model="editForm.category"
              class="form-input"
              maxlength="50"
            />
          </div>
          <div class="form-group">
            <label class="form-label">内容</label>
            <textarea
              v-model="editForm.content"
              class="form-textarea"
              rows="10"
              maxlength="10000"
            ></textarea>
          </div>
        </div>
      </template>
    </template>
    <div v-else class="panel-empty">
      <p>选择一条记录查看详情</p>
    </div>
  </aside>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { marked } from 'marked'
import { useNotesStore } from '../stores/notes.js'

const store = useNotesStore()
const isEditing = ref(false)
const editForm = ref({ title: '', category: '', content: '' })
const formErrors = ref({})

// Auto-enter edit mode when creating a new item (no id)
watch(() => store.selectedItem, (item) => {
  if (item && !item.id) {
    editForm.value = {
      title: item.title || '',
      category: item.category || '',
      content: item.content || '',
    }
    formErrors.value = {}
    isEditing.value = true
  } else {
    isEditing.value = false
  }
})

const emit = defineEmits(['toast', 'confirm-delete'])

const categoryColors = {
  '工作': '#3b82f6',
  '学习': '#22c55e',
  '生活': '#a855f7',
  '想法': '#f59e0b',
}
const defaultColor = '#6b7280'

function categoryColor(cat) {
  return categoryColors[cat] || defaultColor
}

const renderedMarkdown = computed(() => {
  if (!store.selectedItem?.content) return ''
  return marked(store.selectedItem.content)
})

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toISOString().split('T')[0]
}

function startEdit() {
  const item = store.selectedItem
  editForm.value = {
    title: item.title || '',
    category: item.category || '',
    content: item.content || '',
  }
  formErrors.value = {}
  isEditing.value = true
}

function cancelEdit() {
  isEditing.value = false
  formErrors.value = {}
}

function validate() {
  const errors = {}
  if (!editForm.value.title || !editForm.value.title.trim()) {
    errors.title = '标题不能为空'
  }
  if (editForm.value.title.length > 200) {
    errors.title = '标题不能超过200个字符'
  }
  formErrors.value = errors
  return Object.keys(errors).length === 0
}

async function save() {
  if (!validate()) return
  try {
    const data = {
      title: editForm.value.title.trim(),
      category: editForm.value.category.trim(),
      content: editForm.value.content,
    }
    const isCreate = !store.selectedItem.id
    if (isCreate) {
      if (store.selectedType === 'todo') {
        await store.addTodo(data)
      } else {
        await store.addNote(data)
      }
    } else {
      if (store.selectedType === 'todo') {
        await store.saveTodoEdit(store.selectedItem.id, data)
      } else {
        await store.saveNoteEdit(store.selectedItem.id, data)
      }
    }
    isEditing.value = false
    emit('toast', { message: '保存成功', type: 'success' })
  } catch (e) {
    emit('toast', { message: '保存失败', type: 'error' })
  }
}

function requestDelete() {
  emit('confirm-delete', { item: store.selectedItem, type: store.selectedType })
}

async function onToggleComplete() {
  try {
    await store.toggleTodoComplete(store.selectedItem)
  } catch (e) {
    emit('toast', { message: '操作失败', type: 'error' })
  }
}
</script>

<style scoped>
.detail-panel {
  width: 0;
  overflow: hidden;
  background: #fff;
  border-left: 1px solid #eee;
  transition: width 0.25s ease;
  display: flex;
  flex-direction: column;
}
.detail-panel.open {
  width: 360px;
  min-width: 360px;
}
.panel-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  border-bottom: 1px solid #eee;
}
.back-btn {
  border: none;
  background: transparent;
  font-size: 18px;
  cursor: pointer;
  color: #666;
  padding: 0;
}
.panel-title {
  flex: 1;
  font-size: 15px;
  font-weight: 600;
  color: #1a1a1a;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.header-actions {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
}
.action-btn {
  padding: 5px 12px;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
}
.edit-btn { background: #e8f0fe; color: #4f6ef7; }
.save-btn { background: #4f6ef7; color: #fff; }
.cancel-btn { background: #f5f5f5; color: #666; }
.delete-btn { background: #fef2f2; color: #dc2626; }
.panel-body {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}
.meta-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}
.category-tag {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  color: #fff;
}
.date-info {
  font-size: 12px;
  color: #999;
}
.markdown-content {
  font-size: 14px;
  line-height: 1.7;
  color: #333;
}
.markdown-content :deep(h1),
.markdown-content :deep(h2),
.markdown-content :deep(h3) {
  margin-top: 16px;
  margin-bottom: 8px;
  color: #1a1a1a;
}
.markdown-content :deep(pre) {
  background: #f5f7fa;
  padding: 12px;
  border-radius: 6px;
  overflow-x: auto;
  font-size: 12px;
}
.markdown-content :deep(code) {
  font-size: 12px;
}
.markdown-content :deep(p) {
  margin: 0 0 8px 0;
}
.todo-detail-content p {
  color: #666;
  font-size: 14px;
  line-height: 1.6;
}
.completion-status {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}
.completion-status label {
  font-size: 14px;
  color: #333;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}
.completion-status input {
  width: 16px;
  height: 16px;
  accent-color: #4f6ef7;
}
.edit-mode .form-group {
  margin-bottom: 14px;
}
.form-label {
  display: block;
  font-size: 12px;
  color: #666;
  margin-bottom: 4px;
}
.form-input {
  width: 100%;
  padding: 8px 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 13px;
  outline: none;
  box-sizing: border-box;
}
.form-input:focus, .form-textarea:focus {
  border-color: #4f6ef7;
}
.form-input.error {
  border-color: #dc2626;
}
.form-error {
  font-size: 11px;
  color: #dc2626;
}
.form-textarea {
  width: 100%;
  padding: 8px 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 13px;
  outline: none;
  resize: vertical;
  font-family: inherit;
  box-sizing: border-box;
}
.panel-empty {
  padding: 40px 16px;
  text-align: center;
  color: #999;
  font-size: 14px;
}
.loading {
  padding: 40px 16px;
  text-align: center;
  color: #999;
}
</style>
```

---

### Task 14: Build ContentArea component

**Files:**
- Create: `frontend/src/components/ContentArea.vue`

- [ ] **Step 1: Write ContentArea.vue**

Write `frontend/src/components/ContentArea.vue`:
```html
<template>
  <div class="content-area">
    <TopBar @create="startCreate" />
    <TodoList
      v-if="store.activeTab === 'todo'"
      @select="onSelect"
    />
    <NoteCards
      v-if="store.activeTab === 'text'"
      @select="onSelect"
    />
    <Pagination
      v-if="totalPages > 1"
      :current-page="store.currentPage"
      :total-pages="totalPages"
      @page-change="onPageChange"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useNotesStore } from '../stores/notes.js'
import TopBar from './TopBar.vue'
import TodoList from './TodoList.vue'
import NoteCards from './NoteCards.vue'
import Pagination from './Pagination.vue'

const emit = defineEmits(['select', 'create'])
const store = useNotesStore()

const totalPages = computed(() => {
  return Math.ceil(store.totalCount / store.pageSize)
})

function onSelect(item, type) {
  emit('select', item, type)
}

function startCreate() {
  emit('create')
}

async function onPageChange(page) {
  store.setPage(page)
  if (store.activeTab === 'todo') {
    await store.loadTodos()
  } else {
    await store.loadNotes()
  }
}
</script>

<style scoped>
.content-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
  overflow: hidden;
}
</style>
```

---

### Task 15: Build Pagination component

**Files:**
- Create: `frontend/src/components/Pagination.vue`

- [ ] **Step 1: Write Pagination.vue**

Write `frontend/src/components/Pagination.vue`:
```html
<template>
  <div class="pagination">
    <button
      class="page-btn"
      :disabled="currentPage <= 1"
      @click="emit('page-change', currentPage - 1)"
    >上一页</button>
    <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
    <button
      class="page-btn"
      :disabled="currentPage >= totalPages"
      @click="emit('page-change', currentPage + 1)"
    >下一页</button>
  </div>
</template>

<script setup>
defineProps({
  currentPage: { type: Number, required: true },
  totalPages: { type: Number, required: true },
})

const emit = defineEmits(['page-change'])
</script>

<style scoped>
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 12px;
}
.page-btn {
  padding: 6px 16px;
  border: 1px solid #ddd;
  border-radius: 6px;
  background: #fff;
  font-size: 13px;
  color: #4f6ef7;
  cursor: pointer;
}
.page-btn:disabled {
  color: #ccc;
  cursor: not-allowed;
}
.page-btn:not(:disabled):hover {
  background: #f0f4ff;
}
.page-info {
  font-size: 13px;
  color: #666;
}
</style>
```

---

### Task 16: Wire everything together in MainLayout and App.vue

**Files:**
- Modify: `frontend/src/views/MainLayout.vue`
- Modify: `frontend/src/App.vue`

- [ ] **Step 1: Write MainLayout.vue**

Write `frontend/src/views/MainLayout.vue`:
```html
<template>
  <div class="main-layout">
    <Sidebar />
    <ContentArea
      @select="onSelect"
      @create="onCreate"
    />
    <DetailPanel
      @toast="showToast"
      @confirm-delete="onRequestDelete"
    />
    <Toast
      :message="toastMessage"
      :type="toastType"
      :trigger="toastTrigger"
    />
    <ConfirmDialog
      :visible="showConfirm"
      :message="confirmMessage"
      @confirm="onConfirmDelete"
      @cancel="showConfirm = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useNotesStore } from '../stores/notes.js'
import Sidebar from '../components/Sidebar.vue'
import ContentArea from '../components/ContentArea.vue'
import DetailPanel from '../components/DetailPanel.vue'
import Toast from '../components/Toast.vue'
import ConfirmDialog from '../components/ConfirmDialog.vue'

const store = useNotesStore()

// Toast state
const toastMessage = ref('')
const toastType = ref('error')
const toastTrigger = ref(0)

function showToast({ message, type = 'error' }) {
  toastMessage.value = message
  toastType.value = type
  toastTrigger.value++
}

// Confirm dialog state
const showConfirm = ref(false)
const confirmMessage = ref('')
const pendingDelete = ref(null)

function onRequestDelete({ item, type }) {
  pendingDelete.value = { item, type }
  confirmMessage.value = '确定删除这条记录？'
  showConfirm.value = true
}

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

// Select item → open detail
async function onSelect(item, type) {
  try {
    await store.openDetail(item.id, type)
  } catch (e) {
    showToast({ message: '加载详情失败', type: 'error' })
  }
}

// Create new item → open editor in right panel
function onCreate() {
  // Open detail panel in create mode with empty item
  store.selectedItem = {
    title: '',
    category: '',
    content: '',
    is_completed: false,
  }
  store.selectedType = store.activeTab
}

// Tab and category watchers — reload data on change
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

let categoryDebounce = null
watch(() => store.activeCategory, () => {
  clearTimeout(categoryDebounce)
  categoryDebounce = setTimeout(async () => {
    try {
      if (store.activeTab === 'todo') {
        await store.loadTodos()
      } else {
        await store.loadNotes()
      }
    } catch (e) {
      showToast({ message: '加载失败', type: 'error' })
    }
  }, 150)
})

// Initial load
onMounted(async () => {
  try {
    await Promise.all([
      store.loadTodos(),
      store.loadCategories(),
    ])
  } catch (e) {
    showToast({ message: '加载失败', type: 'error' })
  }
})
</script>

<style scoped>
.main-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}
</style>
```

- [ ] **Step 2: Write final App.vue**

Write `frontend/src/App.vue`:
```html
<template>
  <router-view />
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

:root {
  --primary: #4f6ef7;
  --bg-main: #f5f7fa;
  --bg-white: #ffffff;
  --text-heading: #1a1a1a;
  --text-body: #666666;
  --text-aux: #999999;
  --cat-work: #3b82f6;
  --cat-study: #22c55e;
  --cat-life: #a855f7;
  --cat-idea: #f59e0b;
  --radius-sm: 8px;
  --radius-lg: 12px;
  --shadow-card: 0 2px 8px rgba(0, 0, 0, 0.06);
  --shadow-modal: 0 4px 16px rgba(0, 0, 0, 0.1);
  --font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

body {
  font-family: var(--font-family);
  background: var(--bg-main);
  color: var(--text-body);
}

button {
  font-family: inherit;
}

input, textarea {
  font-family: inherit;
}
</style>
```

---

### Task 17: Write .gitignore and README.md

**Files:**
- Create: `.gitignore`
- Create: `README.md`

- [ ] **Step 1: Write .gitignore**

Write `.gitignore`:
```
# Python
__pycache__/
*.py[cod]
*.db
*.sqlite3
backend/venv/
backend/.env

# Node
node_modules/
dist/

# IDE
.vscode/
.idea/

# Superpowers
.superpowers/
```

- [ ] **Step 2: Write README.md**

Write `README.md`:
```markdown
# 网页记事本 (Web Notepad)

A modern note-taking and todo management web app built with Vue3 and Django.

**Stack:** Vue3 + Vite + Pinia + Django + Django REST Framework + SQLite

## Prerequisites

- Python 3.10+
- Node.js 18+
- npm 9+

## Setup & Run

### 1. Backend (Django)

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start server (port 8000)
python manage.py runserver
```

### 2. Frontend (Vue3 + Vite)

```bash
cd frontend

# Install dependencies
npm install

# Start dev server (port 5173)
npm run dev
```

### 3. Open the app

Visit `http://localhost:5173` in your browser.

The Vite dev server proxies `/api/*` requests to Django at port 8000.

## Features

- Create, read, update, delete todos and text notes
- Organize by categories (工作/学习/生活/想法 + custom)
- Markdown rendering for text notes
- Toggle todo completion with optimistic updates
- Search and category filtering
- Pagination
- Responsive three-column layout

## Project Structure

```
web-notepad/
├── backend/          # Django REST API
│   ├── config/       # Settings, URL conf
│   └── notes/        # Models, serializers, views
├── frontend/         # Vue3 SPA
│   └── src/
│       ├── components/  # UI components
│       ├── stores/      # Pinia store
│       ├── api/         # Axios HTTP client
│       └── views/       # Page layouts
└── README.md
```

## Deviations & Known Issues

- No authentication (single-user local use)
- No batch operations
- Google OAuth and AI summary are out of scope
```

---

### Task 18: Integration verification

- [ ] **Step 1: Start Django server**

Run: `cd "d:/project/cs146s/web app/backend" && python manage.py runserver 8000`

Start in a terminal. Verify no errors.

- [ ] **Step 2: Start Vite dev server**

Run: `cd "d:/project/cs146s/web app/frontend" && npm run dev`

Start in another terminal. Verify "ready" message.

- [ ] **Step 3: Smoke test the API**

Run: `curl http://localhost:8000/api/v1/todos`

Expected: `{"count":0,"next":null,"previous":null,"results":[]}`

Run: `curl -X POST http://localhost:8000/api/v1/todos -H "Content-Type: application/json" -d "{\"title\":\"Test\",\"category\":\"工作\"}"`

Expected: JSON response with created todo (id, title, etc.)

- [ ] **Step 4: Smoke test the frontend through proxy**

Run: `curl http://localhost:5173/api/v1/todos`

Expected: `{"count":1,...}` (same data as direct Django call — proxy works)

- [ ] **Step 5: Open browser and test all flows**

Open `http://localhost:5173` and verify:
- TODO list loads with the "Test" todo
- Click "文本" tab → empty notes grid
- Click ＋ → enter title and category → save → item appears in list
- Click an item → detail panel opens on the right
- Click "编辑" → edit title → "保存" → detail updates
- Click "删除" → confirm dialog → delete → item removed
- Toggle checkbox → strikethrough applied
- Click sidebar categories → filtering works
- Type in search box → filtering works
- Pagination appears when >20 items
- Refresh page → data persists

---

### Task 19: Run all backend tests

Run: `cd "d:/project/cs146s/web app/backend" && python manage.py test notes -v 2`

Expected: All 30 tests pass with no failures.
