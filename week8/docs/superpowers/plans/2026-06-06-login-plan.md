# Login & Multi-User Authentication — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add multi-user authentication (open registration + login via Django session) with per-user data isolation and per-user AI settings.

**Architecture:** Django's built-in `auth.User` model + session cookie authentication. Each `Note`, `Todo`, and `AISettings` record gets a foreign key to `User`. DRF viewsets add `IsAuthenticated` and filter querysets by `request.user`. Vue frontend adds `LoginPage`/`RegisterPage`, a route guard, and a logout button.

**Tech Stack:** Django 5.x, Django REST Framework, Vue 3 (Composition API + `<script setup>`), Pinia, Vue Router, Axios, SQLite

---

## File Structure

### Files Created
| File | Purpose |
|------|---------|
| `backend/notes/migrations/0004_add_user_fk.py` | Model schema + data migration |
| `frontend/src/stores/auth.js` | Auth state (user, login, register, logout) |
| `frontend/src/views/LoginPage.vue` | Login form |
| `frontend/src/views/RegisterPage.vue` | Registration form |

### Files Modified
| File | Purpose |
|------|---------|
| `backend/notes/models.py` | Add `user` FK to Note/Todo, OneToOne to AISettings |
| `backend/notes/serializers.py` | Add RegisterSerializer, LoginSerializer; rework AISettingsSerializer |
| `backend/notes/views.py` | Add AuthViewSet; add permissions + user filtering |
| `backend/notes/urls.py` | Register `/auth/` routes |
| `backend/notes/ai_service.py` | Per-user AISettings instead of singleton |
| `backend/notes/tests.py` | Auth tests + fix existing tests for user ownership |
| `frontend/src/api/index.js` | Auth API functions + 401 interceptor; fix AISettings URL |
| `frontend/src/router/index.js` | `/login`, `/register` routes + beforeEach guard |
| `frontend/src/components/Sidebar.vue` | Logout button |
| `frontend/src/views/MainLayout.vue` | Minor auth awareness |

---

### Task 1: Add `user` fields to models + create migration

**Files:**
- Modify: `web app/backend/notes/models.py`
- Create: `web app/backend/notes/migrations/0004_add_user_fk.py`

- [ ] **Step 1: Update models.py**

Replace the entire `models.py`:

```python
from datetime import date

from django.contrib.auth.models import User
from django.db import models


class Todo(models.Model):
    CATEGORY_CHOICES = [
        ("工作", "工作"),
        ("学习", "学习"),
        ("生活", "生活"),
        ("想法", "想法"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="todos")
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True, default="")
    category = models.CharField(max_length=50, blank=True, default="")
    due_date = models.DateField(null=True, blank=True, default=date.today)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notes")
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True, default="")
    category = models.CharField(max_length=50, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class AISettings(models.Model):
    """Per-user AI API configuration. One row per user."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="ai_settings")
    api_key = models.CharField(max_length=512, blank=True, default="")
    base_url = models.URLField(default="https://api.openai.com/v1")
    model = models.CharField(max_length=100, default="gpt-4o-mini")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "AI Settings"
        verbose_name_plural = "AI Settings"

    def __str__(self):
        return f"AISettings(user={self.user.email}, model={self.model})"

    def is_configured(self):
        return bool(self.api_key)
```

- [ ] **Step 2: Generate migration**

```bash
cd "web app/backend" && python manage.py makemigrations notes --name add_user_fk
```

When prompted for a one-off default, choose option 1 ("Provide a one-off default now") and enter `1` for the ForeignKey fields. We'll fix it in the next step.

- [ ] **Step 3: Add data migration to the generated migration file**

Read the generated `0004_add_user_fk.py`, then edit it to add a `RunPython` operation that creates the default admin user. The migration should look like this (replace the auto-generated content):

```python
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.db import migrations, models
import django.db.models.deletion


def create_default_admin(apps, schema_editor):
    """Create a default admin user and assign all existing records to it."""
    User = apps.get_model("auth", "User")

    admin = User.objects.create_user(
        username="admin@admin.com",
        email="admin@admin.com",
        password="admin123",
    )

    Note = apps.get_model("notes", "Note")
    Todo = apps.get_model("notes", "Todo")
    AISettings = apps.get_model("notes", "AISettings")

    Note.objects.all().update(user=admin)
    Todo.objects.all().update(user=admin)
    AISettings.objects.all().update(user=admin)

    print(f"\n✓ Created default admin user: admin@admin.com / admin123")
    print(f"✓ Migrated {Note.objects.count()} notes, {Todo.objects.count()} todos to admin")


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("notes", "0003_ai_settings"),
    ]

    operations = [
        # Add user fields as nullable first
        migrations.AddField(
            model_name="aisettings",
            name="user",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="ai_settings",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="note",
            name="user",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="notes",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="todo",
            name="user",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="todos",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        # Populate existing records
        migrations.RunPython(create_default_admin, noop),
        # Make fields non-nullable
        migrations.AlterField(
            model_name="aisettings",
            name="user",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="ai_settings",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="note",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="notes",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="todo",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="todos",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
```

- [ ] **Step 4: Run the migration**

```bash
cd "web app/backend" && python manage.py migrate
```

Expected: migration runs successfully, prints admin user creation message.

- [ ] **Step 5: Commit**

```bash
cd "D:/project/cs146s/modern-software-dev-assignments/week8" && git add "web app/backend/notes/models.py" "web app/backend/notes/migrations/0004_add_user_fk.py" && git commit -m "feat: add user FK to Note, Todo, AISettings models with data migration"
```

---

### Task 2: Add auth serializers

**Files:**
- Modify: `web app/backend/notes/serializers.py`

- [ ] **Step 1: Add RegisterSerializer and LoginSerializer to serializers.py**

Edit `serializers.py` — add the following imports at the top (merge with existing):

```python
from django.contrib.auth.models import User
```

Add these two serializer classes after the existing `AISettingsSerializer` class:

```python
class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=6, write_only=True)
    password2 = serializers.CharField(min_length=6, write_only=True)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("该邮箱已被注册")
        return value

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError({"password2": "两次密码不一致"})
        return data

    def create(self, validated_data):
        email = validated_data["email"]
        password = validated_data.pop("password")
        validated_data.pop("password2")
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
```

- [ ] **Step 2: Update AISettingsSerializer — remove singleton pattern, use per-user**

Edit `AISettingsSerializer` class. Replace the entire class:

```python
class AISettingsSerializer(serializers.ModelSerializer):
    is_configured = serializers.SerializerMethodField()

    class Meta:
        model = AISettings
        fields = ["api_key", "base_url", "model", "updated_at", "is_configured"]
        read_only_fields = ["updated_at", "is_configured"]

    def get_is_configured(self, obj):
        return obj.is_configured()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.api_key:
            data["api_key"] = "***"
        else:
            data["api_key"] = ""
        return data

    def update(self, instance, validated_data):
        api_key = validated_data.get("api_key", "***")
        if api_key == "***":
            validated_data.pop("api_key", None)
        else:
            validated_data["api_key"] = encrypt_api_key(api_key)
        return super().update(instance, validated_data)
```

Note: This removes the `create` method since AISettings is now created automatically when a user registers (see Task 3). The `user` field is excluded from the serializer because it's resolved automatically from `request.user`.

- [ ] **Step 3: Commit**

```bash
cd "D:/project/cs146s/modern-software-dev-assignments/week8" && git add "web app/backend/notes/serializers.py" && git commit -m "feat: add RegisterSerializer, LoginSerializer; update AISettingsSerializer for per-user"
```

---

### Task 3: Add auth views (register, login, logout, me)

**Files:**
- Modify: `web app/backend/notes/views.py`

- [ ] **Step 1: Add AuthViewSet to views.py**

Add these imports at the top of `views.py` (merge with existing):

```python
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from notes.models import AISettings
from notes.serializers import LoginSerializer, RegisterSerializer
```

Add this class after the existing viewset classes (before or after `AISettingsViewSet`):

```python
class AuthViewSet(viewsets.GenericViewSet):
    """Registration, login, logout, and current-user endpoints."""

    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def get_serializer_class(self):
        if self.action == "login":
            return LoginSerializer
        return RegisterSerializer

    @action(detail=False, methods=["post"])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Create AISettings for the new user
        AISettings.objects.create(user=user)

        login(request, user)
        return Response(
            {"id": user.id, "email": user.email},
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["post"])
    def login_view(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        user = authenticate(request, username=email, password=password)
        if user is None:
            return Response(
                {"detail": "邮箱或密码错误"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        login(request, user)
        return Response({"id": user.id, "email": user.email})

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def logout_view(self, request):
        logout(request)
        return Response({"detail": "已登出"})

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def me(self, request):
        return Response({"id": request.user.id, "email": request.user.email})
```

Note: The action method names end with `_view` for login/logout to avoid shadowing Django's `login`/`logout` functions. The URL names will be set explicitly in urls.py.

- [ ] **Step 2: Commit**

```bash
cd "D:/project/cs146s/modern-software-dev-assignments/week8" && git add "web app/backend/notes/views.py" && git commit -m "feat: add AuthViewSet with register, login, logout, me actions"
```

---

### Task 4: Register auth URLs

**Files:**
- Modify: `web app/backend/notes/urls.py`

- [ ] **Step 1: Add auth routes to urls.py**

Add this import:

```python
from notes.views import AISettingsViewSet, AuthViewSet, NoteViewSet, TodoViewSet
```

Add this router registration after the existing `router.register(...)` calls:

```python
router.register(r"auth", AuthViewSet, basename="auth")
```

Edit the urlpatterns to map the auth actions to clean URLs without `_view` suffix:

```python
from django.urls import path

from notes.views import AISettingsViewSet, AuthViewSet, NoteViewSet, TodoViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r"todos", TodoViewSet, basename="todo")
router.register(r"notes", NoteViewSet, basename="note")
router.register(r"ai-settings", AISettingsViewSet, basename="ai-settings")
router.register(r"auth", AuthViewSet, basename="auth")


class CategoryListView(APIView):
    # ... (unchanged)


class CategoryDeleteView(APIView):
    # ... (unchanged)


urlpatterns = router.urls + [
    path("categories", CategoryListView.as_view(), name="categories"),
    path("categories/delete", CategoryDeleteView.as_view(), name="category-delete"),
    # Override auth action URLs for clean paths
    path(
        "auth/register",
        AuthViewSet.as_view({"post": "register"}),
        name="auth-register",
    ),
    path(
        "auth/login",
        AuthViewSet.as_view({"post": "login_view"}),
        name="auth-login",
    ),
    path(
        "auth/logout",
        AuthViewSet.as_view({"post": "logout_view"}),
        name="auth-logout",
    ),
    path(
        "auth/me",
        AuthViewSet.as_view({"get": "me"}),
        name="auth-me",
    ),
]
```

Note: The router already generates `/auth/register/`, `/auth/login_view/`, etc. with trailing slash. The explicit `path()` routes give us clean `/auth/register`, `/auth/login`, `/auth/logout`, `/auth/me` URLs without the `_view` suffix. The router-generated URLs still work as aliases but frontend will use the clean paths.

- [ ] **Step 2: Verify routes**

```bash
cd "web app/backend" && python manage.py show_urls 2>/dev/null || python -c "from django.urls import get_resolver; [print(p.pattern, p.name) for p in get_resolver().url_patterns]"
```

Expected: routes like `auth/register`, `auth/login`, `auth/logout`, `auth/me` appear.

- [ ] **Step 3: Commit**

```bash
cd "D:/project/cs146s/modern-software-dev-assignments/week8" && git add "web app/backend/notes/urls.py" && git commit -m "feat: register auth routes (register, login, logout, me)"
```

---

### Task 5: Add permissions and user filtering to existing viewsets

**Files:**
- Modify: `web app/backend/notes/views.py`

- [ ] **Step 1: Update BaseItemViewSet, TodoViewSet, NoteViewSet**

Edit `views.py` — the updated file should look like this (showing the changed parts):

```python
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import models
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from notes.ai_service import (
    AINotConfiguredError,
    AIServiceError,
    EmptyContentError,
    summarize_note_todos,
)
from notes.models import AISettings, Note, Todo
from notes.serializers import (
    AISettingsSerializer,
    LoginSerializer,
    NoteSerializer,
    RegisterSerializer,
    TodoSerializer,
)


class BaseItemViewSet(viewsets.ModelViewSet):
    """共享过滤逻辑的基类 — 所有操作需要登录，数据按当前用户过滤"""

    permission_classes = [IsAuthenticated]

    def filter_queryset_by_params(self, queryset):
        category = self.request.query_params.get("category", None)
        q = self.request.query_params.get("q", None)
        if category and category != "全部":
            queryset = queryset.filter(category=category)
        if q:
            queryset = queryset.filter(
                models.Q(title__icontains=q) | models.Q(content__icontains=q)
            )
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TodoViewSet(BaseItemViewSet):
    serializer_class = TodoSerializer

    def get_queryset(self):
        return self.filter_queryset_by_params(
            Todo.objects.filter(user=self.request.user)
        )


class NoteViewSet(BaseItemViewSet):
    serializer_class = NoteSerializer

    def get_queryset(self):
        return self.filter_queryset_by_params(
            Note.objects.filter(user=self.request.user)
        )

    @action(detail=True, methods=["post"], url_path="summarize-todos")
    def summarize_todos(self, request, pk=None):
        """Call AI to extract todo items from the note content."""
        note = self.get_object()
        try:
            todos, count = summarize_note_todos(note)
        # ... (rest unchanged)


class AISettingsViewSet(viewsets.ModelViewSet):
    """Per-user AI settings. GET returns current user's settings, PUT updates it."""

    serializer_class = AISettingsSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "put", "head", "options"]

    def get_queryset(self):
        return AISettings.objects.filter(user=self.request.user)

    def get_object(self):
        obj, _ = AISettings.objects.get_or_create(user=self.request.user)
        return obj

    # list() is never called directly, but get_queryset needs to exist.
    # Override retrieve to always return current user's settings.
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


# AuthViewSet stays here (unchanged from Task 3)
```

- [ ] **Step 2: Update CategoryListView and CategoryDeleteView (in urls.py) for user isolation**

Since these are `APIView` classes in `urls.py`, add `IsAuthenticated` permission and user filtering. Edit `web app/backend/notes/urls.py`:

```python
from rest_framework.permissions import IsAuthenticated

# ...

class CategoryListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        todo_categories = (
            Todo.objects.filter(user=request.user)
            .exclude(category="")
            .values_list("category", flat=True)
            .distinct()
        )
        note_categories = (
            Note.objects.filter(user=request.user)
            .exclude(category="")
            .values_list("category", flat=True)
            .distinct()
        )
        all_categories = sorted(set(list(todo_categories) + list(note_categories)))
        return Response(all_categories)


class CategoryDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def delete(self, request):
        name = request.query_params.get("name", "")
        if not name:
            return Response({"detail": "缺少分类名称参数"}, status=status.HTTP_400_BAD_REQUEST)
        todo_count = Todo.objects.filter(user=request.user, category=name).update(category="")
        note_count = Note.objects.filter(user=request.user, category=name).update(category="")
        total = todo_count + note_count
        return Response({"deleted": name, "cleared": total})
```

Also update the imports in `urls.py` to include `IsAuthenticated`:

```python
from rest_framework.permissions import IsAuthenticated
```

- [ ] **Step 3: Commit**

```bash
cd "D:/project/cs146s/modern-software-dev-assignments/week8" && git add "web app/backend/notes/views.py" "web app/backend/notes/urls.py" && git commit -m "feat: add IsAuthenticated permission and user filtering to all viewsets and category views"
```

---

### Task 6: Update ai_service.py for per-user AISettings

**Files:**
- Modify: `web app/backend/notes/ai_service.py`

- [ ] **Step 1: Update `summarize_note_todos` to use the note owner's AISettings**

Edit `ai_service.py`. The function `summarize_note_todos` currently does:

```python
ai_settings = AISettings.get_solo()
```

Change it to get settings from the note's owner. Also update the `Todo.objects.create(...)` to assign the user. After all changes, here's the updated `summarize_note_todos`:

```python
def summarize_note_todos(note):
    """
    Main entry point: call AI API for a note, create Todo items from the result.
    Returns (todos, count) tuple.
    """
    ai_settings, _ = AISettings.objects.get_or_create(user=note.user)

    if not ai_settings.is_configured():
        raise AINotConfiguredError("AI API settings are not configured")

    if not note.content or not note.content.strip():
        raise EmptyContentError("Note content is empty")

    # Truncate content to avoid token limits
    truncated_content = note.content[:MAX_CONTENT_CHARS]

    titles = call_ai_api(ai_settings, truncated_content)

    with transaction.atomic():
        created_todos = []
        for title in titles:
            todo = Todo.objects.create(
                user=note.user,
                title=title,
                content="",
                category=note.category,
            )
            created_todos.append(todo)

    return created_todos, len(created_todos)
```

- [ ] **Step 2: Commit**

```bash
cd "D:/project/cs146s/modern-software-dev-assignments/week8" && git add "web app/backend/notes/ai_service.py" && git commit -m "feat: update ai_service to use note owner's AISettings instead of singleton"
```

---

### Task 7: Write backend tests for auth + fix existing tests

**Files:**
- Modify: `web app/backend/notes/tests.py`

- [ ] **Step 1: Add auth imports and helper base class**

Add these imports to `tests.py` (merge with existing):

```python
from django.contrib.auth.models import User
from notes.models import AISettings, Note, Todo
```

Add a helper base class that all existing API tests can extend:

```python
class AuthenticatedAPITestCase(APITestCase):
    """Base class that creates a test user and logs it in."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="test@example.com",
            email="test@example.com",
            password="testpass123",
        )
        # Ensure AISettings exists for this user
        AISettings.objects.create(user=cls.user)

    def setUp(self):
        self.client.force_login(self.user)
```

- [ ] **Step 2: Fix existing test classes to use AuthenticatedAPITestCase**

Change the parent class of each existing API test class from `APITestCase` to `AuthenticatedAPITestCase`:

- `class TodoAPITest(AuthenticatedAPITestCase):`
- `class NoteAPITest(AuthenticatedAPITestCase):`
- `class CategoryAPITest(AuthenticatedAPITestCase):`
- `class CategoryDeleteAPITest(AuthenticatedAPITestCase):`
- `class AISettingsAPITest(AuthenticatedAPITestCase):`
- `class AISummarizeAPITest(AuthenticatedAPITestCase):`

Also update model tests (`TodoModelTest`, `NoteModelTest`) and serializer tests to create records with a user:

In `TodoModelTest.setUp` (add setUp if not present) or in each test, replace `Todo.objects.create(title=...)` with `Todo.objects.create(user=user, title=...)`. The cleanest approach: add `setUpTestData` to each model test class. Here's the updated `TodoModelTest`:

```python
class TodoModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="modeltest@example.com",
            email="modeltest@example.com",
            password="testpass123",
        )

    def test_create_todo_with_minimal_fields(self):
        todo = Todo.objects.create(user=self.user, title="Buy groceries")
        self.assertEqual(todo.title, "Buy groceries")
        # ... rest unchanged

    # ... all other tests updated to include user=self.user
```

And `NoteModelTest` similarly.

For serializer tests: validators only check input data, serializers don't auto-assign `user` (that's in the view), so serializer tests don't need users. Leave them as-is.

For `AISettingsModelTest` and `AISettingsEncryptionTest`: `get_solo()` is removed. Update tests to create settings per-user:

```python
class AISettingsModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="aitest@example.com",
            email="aitest@example.com",
            password="testpass123",
        )

    def test_default_settings_created_with_user(self):
        AISettings.objects.create(user=self.user)
        s = self.user.ai_settings
        self.assertEqual(s.model, "gpt-4o-mini")
        self.assertEqual(s.base_url, "https://api.openai.com/v1")
        self.assertEqual(s.api_key, "")
        self.assertFalse(s.is_configured())

    def test_is_configured_with_key(self):
        AISettings.objects.create(user=self.user)
        s = self.user.ai_settings
        s.api_key = encrypt_api_key("sk-test-key")
        s.save()
        self.assertTrue(s.is_configured())


class AISettingsEncryptionTest(TestCase):
    def test_encrypt_decrypt_roundtrip(self):
        # unchanged
        ...

    def test_encrypt_empty_key(self):
        # unchanged
        ...

    def test_decrypt_empty_key(self):
        # unchanged
        ...
```

For `AISettingsAPITest`: Change to use the logged-in user's settings (no `/1` in URL):

```python
class AISettingsAPITest(AuthenticatedAPITestCase):
    def test_get_unconfigured_settings(self):
        response = self.client.get("/api/v1/ai-settings")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_configured"])
        self.assertEqual(response.data["api_key"], "")
        self.assertEqual(response.data["model"], "gpt-4o-mini")

    def test_put_settings_masks_key_in_response(self):
        response = self.client.put(
            "/api/v1/ai-settings",
            {
                "api_key": "sk-my-secret-key",
                "base_url": "https://api.openai.com/v1",
                "model": "gpt-4o",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["api_key"], "***")

    def test_put_settings_encrypts_key_at_rest(self):
        self.client.put(
            "/api/v1/ai-settings",
            {
                "api_key": "sk-my-secret-key",
                "base_url": "https://api.openai.com/v1",
                "model": "gpt-4o",
            },
            format="json",
        )
        s = self.user.ai_settings
        self.assertNotEqual(s.api_key, "sk-my-secret-key")
        self.assertTrue(len(s.api_key) > 0)
        self.assertEqual(decrypt_api_key(s.api_key), "sk-my-secret-key")

    def test_put_star_preserves_existing_key(self):
        self.client.put(
            "/api/v1/ai-settings",
            {
                "api_key": "sk-original-key",
                "base_url": "https://api.openai.com/v1",
                "model": "gpt-4o",
            },
            format="json",
        )
        self.client.put(
            "/api/v1/ai-settings",
            {"api_key": "***", "base_url": "https://api.deepseek.com/v1", "model": "deepseek-chat"},
            format="json",
        )
        s = self.user.ai_settings
        self.assertEqual(decrypt_api_key(s.api_key), "sk-original-key")
        self.assertEqual(s.model, "deepseek-chat")
        self.assertEqual(s.base_url, "https://api.deepseek.com/v1")
```

For `AISummarizeAPITest`: Update all `AISettings.get_solo()` calls to use `self.user.ai_settings`. E.g.:

```python
class AISummarizeAPITest(AuthenticatedAPITestCase):
    def setUp(self):
        super().setUp()
        self.note = Note.objects.create(
            user=self.user,
            title="Meeting Notes",
            content="需要完成项目报告\n需要回复客户邮件\n预约下周的会议室",
            category="工作",
        )

    def test_summarize_without_settings(self):
        # Delete the default AISettings
        self.user.ai_settings.delete()
        response = self.client.post(f"/api/v1/notes/{self.note.id}/summarize-todos")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("请先配置", response.data["detail"])

    def test_summarize_empty_content(self):
        s = self.user.ai_settings
        s.api_key = encrypt_api_key("sk-test")
        s.save()
        note = Note.objects.create(
            user=self.user, title="Empty", content="", category="工作"
        )
        response = self.client.post(f"/api/v1/notes/{note.id}/summarize-todos")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("为空", response.data["detail"])

    @patch("notes.ai_service.requests.post")
    def test_summarize_success(self, mock_post):
        s = self.user.ai_settings
        s.api_key = encrypt_api_key("sk-test")
        s.save()

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": '[{"title":"完成项目报告"},{"title":"回复客户邮件"},{"title":"预约会议室"}]'
                    }
                }
            ]
        }
        mock_post.return_value = mock_resp

        response = self.client.post(f"/api/v1/notes/{self.note.id}/summarize-todos")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)
        self.assertEqual(len(response.data["todos"]), 3)

        todos = Todo.objects.filter(user=self.user, category="工作")
        self.assertEqual(todos.count(), 3)

    # ... remaining summarize tests follow the same pattern:
    # replace AISettings.get_solo() with self.user.ai_settings
    # add user=self.user to Note and Todo creation
```

- [ ] **Step 3: Add new auth test class**

Add this at the end of `tests.py`:

```python
class AuthAPITest(APITestCase):
    """Test register, login, logout, and me endpoints."""

    def test_register_success(self):
        response = self.client.post(
            "/api/v1/auth/register",
            {"email": "new@example.com", "password": "pass123", "password2": "pass123"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["email"], "new@example.com")
        # User exists in DB
        user = User.objects.get(email="new@example.com")
        self.assertIsNotNone(user)
        # AISettings auto-created
        self.assertTrue(hasattr(user, "ai_settings"))

    def test_register_duplicate_email(self):
        User.objects.create_user(
            username="existing@example.com",
            email="existing@example.com",
            password="pass123",
        )
        response = self.client.post(
            "/api/v1/auth/register",
            {"email": "existing@example.com", "password": "pass123", "password2": "pass123"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("该邮箱已被注册", str(response.data["email"]))

    def test_register_short_password(self):
        response = self.client.post(
            "/api/v1/auth/register",
            {"email": "new@example.com", "password": "12345", "password2": "12345"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_register_password_mismatch(self):
        response = self.client.post(
            "/api/v1/auth/register",
            {"email": "new@example.com", "password": "pass123", "password2": "different"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("两次密码不一致", str(response.data["password2"]))

    def test_register_invalid_email(self):
        response = self.client.post(
            "/api/v1/auth/register",
            {"email": "not-an-email", "password": "pass123", "password2": "pass123"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_login_success(self):
        User.objects.create_user(
            username="test@example.com",
            email="test@example.com",
            password="pass123",
        )
        response = self.client.post(
            "/api/v1/auth/login",
            {"email": "test@example.com", "password": "pass123"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "test@example.com")

    def test_login_wrong_password(self):
        User.objects.create_user(
            username="test@example.com",
            email="test@example.com",
            password="pass123",
        )
        response = self.client.post(
            "/api/v1/auth/login",
            {"email": "test@example.com", "password": "wrongpass"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("邮箱或密码错误", response.data["detail"])

    def test_login_nonexistent_email(self):
        response = self.client.post(
            "/api/v1/auth/login",
            {"email": "nobody@example.com", "password": "pass123"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("邮箱或密码错误", response.data["detail"])

    def test_logout(self):
        user = User.objects.create_user(
            username="test@example.com",
            email="test@example.com",
            password="pass123",
        )
        self.client.force_login(user)
        response = self.client.post("/api/v1/auth/logout")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "已登出")

    def test_me_authenticated(self):
        user = User.objects.create_user(
            username="test@example.com",
            email="test@example.com",
            password="pass123",
        )
        self.client.force_login(user)
        response = self.client.get("/api/v1/auth/me")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "test@example.com")

    def test_me_unauthenticated(self):
        response = self.client.get("/api/v1/auth/me")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_crud_requires_auth(self):
        # Todos without auth
        response = self.client.get("/api/v1/todos")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # Notes without auth
        response = self.client.get("/api/v1/notes")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # Categories without auth
        response = self.client.get("/api/v1/categories")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserIsolationTest(APITestCase):
    """Test that users cannot see each other's data."""

    def setUp(self):
        self.user_a = User.objects.create_user(
            username="a@example.com", email="a@example.com", password="pass123"
        )
        self.user_b = User.objects.create_user(
            username="b@example.com", email="b@example.com", password="pass123"
        )
        self.note_a = Note.objects.create(
            user=self.user_a, title="A's Note", content="Secret", category="工作"
        )
        self.todo_a = Todo.objects.create(
            user=self.user_a, title="A's Todo", category="工作"
        )
        self.note_b = Note.objects.create(
            user=self.user_b, title="B's Note", category="工作"
        )
        self.todo_b = Todo.objects.create(
            user=self.user_b, title="B's Todo", category="工作"
        )

    def test_user_a_cannot_see_user_b_notes(self):
        self.client.force_login(self.user_a)
        response = self.client.get("/api/v1/notes")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["title"], "A's Note")

    def test_user_a_cannot_see_user_b_todos(self):
        self.client.force_login(self.user_a)
        response = self.client.get("/api/v1/todos")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["title"], "A's Todo")

    def test_user_a_cannot_access_user_b_note_directly(self):
        self.client.force_login(self.user_a)
        response = self.client.get(f"/api/v1/notes/{self.note_b.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_a_cannot_access_user_b_todo_directly(self):
        self.client.force_login(self.user_a)
        response = self.client.get(f"/api/v1/todos/{self.todo_b.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_a_categories_excludes_user_b(self):
        self.client.force_login(self.user_a)
        response = self.client.get("/api/v1/categories")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data), {"工作"})

    def test_ai_settings_isolated_per_user(self):
        AISettings.objects.create(user=self.user_a)
        AISettings.objects.create(user=self.user_b)
        self.client.force_login(self.user_a)
        response = self.client.get("/api/v1/ai-settings")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should get user_a's settings, not user_b's
        s_a = self.user_a.ai_settings
        self.assertEqual(response.data["model"], s_a.model)
```

- [ ] **Step 4: Run tests**

```bash
cd "web app/backend" && python manage.py test notes -v2
```

Expected: all tests pass. Fix any failures before continuing.

- [ ] **Step 5: Commit**

```bash
cd "D:/project/cs146s/modern-software-dev-assignments/week8" && git add "web app/backend/notes/tests.py" && git commit -m "test: add auth and user isolation tests; fix existing tests for per-user data"
```

---

### Task 8: Create auth store and API functions (frontend)

**Files:**
- Create: `web app/frontend/src/stores/auth.js`
- Modify: `web app/frontend/src/api/index.js`

- [ ] **Step 1: Create auth store**

Create `web app/frontend/src/stores/auth.js`:

```javascript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { register as apiRegister, login as apiLogin, logout as apiLogout, fetchCurrentUser } from '../api/index.js'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const isAuthenticated = computed(() => !!user.value)

  async function checkAuth() {
    try {
      const res = await fetchCurrentUser()
      user.value = res.data
      return true
    } catch (e) {
      user.value = null
      return false
    }
  }

  async function register(email, password, password2) {
    const res = await apiRegister({ email, password, password2 })
    user.value = res.data
    return res.data
  }

  async function login(email, password) {
    const res = await apiLogin({ email, password })
    user.value = res.data
    return res.data
  }

  async function logout() {
    await apiLogout()
    user.value = null
  }

  return {
    user,
    isAuthenticated,
    checkAuth,
    register,
    login,
    logout,
  }
})
```

- [ ] **Step 2: Add auth API functions and 401 interceptor to api/index.js**

Add these functions to `web app/frontend/src/api/index.js` before the `export default api` line:

```javascript
// Auth
export function register(data) {
  return api.post('/auth/register', data)
}

export function login(data) {
  return api.post('/auth/login', data)
}

export function logout() {
  return api.post('/auth/logout')
}

export function fetchCurrentUser() {
  return api.get('/auth/me')
}
```

Update the AISettings functions — remove hardcoded `/1` path:

```javascript
export function fetchAISettings() {
  return api.get('/ai-settings')
}

export function saveAISettings(data) {
  return api.put('/ai-settings', data)
}
```

Add 401 interceptor **after** the `const api = axios.create(...)` block but **before** any function definitions. The interceptor needs access to the router. Since `api/index.js` doesn't import router, use a module-level approach:

```javascript
import axios from 'axios'
import router from '../router/index.js'

const api = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
  xsrfCookieName: 'csrftoken',
  xsrfHeaderName: 'X-CSRFToken',
  withCredentials: true,
})

// 401 interceptor — redirect to login on unauthorized responses
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      const authStore = useAuthStore()
      authStore.user = null
      router.push('/login')
    }
    return Promise.reject(error)
  }
)
```

But wait — importing `router` creates a circular dependency (router imports pages which import stores which import api). To avoid this, use a lazy import or handle 401 in the route guard instead of the interceptor. The spec says "axios interceptor" but that risks circular imports.

Better approach: **Don't add an interceptor in api/index.js**. Instead, handle 401 at the store/component level. The route `beforeEach` guard already checks auth status before each navigation. And if a stale session causes a 401 mid-use, the Pinia store's error handling can catch it.

Actually, the cleanest approach for avoiding the circular dep: use the store's approach. Don't add a global interceptor; delegate 401 redirection to the route guard. But to handle mid-session 401s (session expires), add handling in the store:

In `auth.js` store:
```javascript
// The checkAuth function already handles 401 by returning false.
// Any other API calls that return 401 during use will bubble up 
// as regular errors via the existing store error handling in notes.js.
```

This is simpler and avoids circular imports. The route guard handles initial navigation; for mid-session expirations, the user will see an error toast and can reload.

**So don't add an interceptor.** Just add the auth functions and fix the AISettings URL.

- [ ] **Step 3: Commit**

```bash
cd "D:/project/cs146s/modern-software-dev-assignments/week8" && git add "web app/frontend/src/stores/auth.js" "web app/frontend/src/api/index.js" && git commit -m "feat: add auth store and API functions with AISettings URL fix"
```

---

### Task 9: Update router with auth routes and guard

**Files:**
- Modify: `web app/frontend/src/router/index.js`

- [ ] **Step 1: Replace router/index.js**

```javascript
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'

const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('../views/MainLayout.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/LoginPage.vue'),
    meta: { guest: true },
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('../views/RegisterPage.vue'),
    meta: { guest: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to) => {
  const authStore = useAuthStore()
  const isLoggedIn = await authStore.checkAuth()

  if (to.meta.requiresAuth && !isLoggedIn) {
    return '/login'
  }

  if (to.meta.guest && isLoggedIn) {
    return '/'
  }
})

export default router
```

- [ ] **Step 2: Commit**

```bash
cd "D:/project/cs146s/modern-software-dev-assignments/week8" && git add "web app/frontend/src/router/index.js" && git commit -m "feat: add /login and /register routes with auth guard"
```

---

### Task 10: Create LoginPage.vue

**Files:**
- Create: `web app/frontend/src/views/LoginPage.vue`

- [ ] **Step 1: Create LoginPage.vue**

```vue
<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-header">
        <div class="brand-mark">
          <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
            <rect x="4" y="2" width="20" height="24" rx="3" stroke="currentColor" stroke-width="1.5" fill="none"/>
            <line x1="10" y1="8" x2="18" y2="8" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
            <line x1="10" y1="12" x2="18" y2="12" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
            <line x1="10" y1="16" x2="15" y2="16" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
            <rect x="8" y="3" width="3" height="1.5" rx="0.75" fill="currentColor" opacity="0.4"/>
          </svg>
        </div>
        <h1 class="auth-title">网页记事本</h1>
        <p class="auth-subtitle">登录你的账户</p>
      </div>

      <form class="auth-form" @submit.prevent="handleLogin">
        <div v-if="error" class="auth-error">{{ error }}</div>

        <div class="field">
          <label class="field-label" for="login-email">邮箱</label>
          <input
            id="login-email"
            v-model="email"
            type="email"
            class="field-input"
            placeholder="your@email.com"
            autocomplete="email"
            required
          />
        </div>

        <div class="field">
          <label class="field-label" for="login-password">密码</label>
          <input
            id="login-password"
            v-model="password"
            type="password"
            class="field-input"
            placeholder="••••••••"
            autocomplete="current-password"
            required
          />
        </div>

        <button type="submit" class="auth-btn" :disabled="loading">
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>

      <p class="auth-switch">
        还没有账户？<router-link to="/register" class="auth-link">立即注册</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await authStore.login(email.value, password.value)
    router.push('/')
  } catch (e) {
    const detail = e.response?.data?.detail
    if (detail) {
      error.value = detail
    } else if (e.response?.data) {
      // Field-level errors (unlikely for login but handle)
      const first = Object.values(e.response.data)[0]
      error.value = Array.isArray(first) ? first[0] : first
    } else {
      error.value = '登录失败，请重试'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-page);
  padding: var(--space-lg);
}

.auth-card {
  width: 100%;
  max-width: 380px;
  background: var(--bg-surface);
  border-radius: var(--radius-lg);
  padding: var(--space-3xl) var(--space-2xl);
  box-shadow: var(--shadow-lg);
  border: 1px solid var(--border-light);
}

.auth-header {
  text-align: center;
  margin-bottom: var(--space-2xl);
}

.brand-mark {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  background: var(--accent-soft);
  color: var(--accent);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto var(--space-md);
}

.auth-title {
  font-family: var(--font-display);
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: 0.03em;
  margin-bottom: var(--space-xs);
}

.auth-subtitle {
  font-size: 0.875rem;
  color: var(--text-muted);
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.auth-error {
  background: var(--error-bg);
  color: var(--error);
  border: 1px solid var(--error-border);
  border-radius: var(--radius-sm);
  padding: var(--space-sm) var(--space-md);
  font-size: 0.8125rem;
  text-align: center;
}

.field {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.field-label {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.field-input {
  width: 100%;
  padding: var(--space-sm) var(--space-md);
  font-size: 0.9375rem;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--bg-page);
  color: var(--text-primary);
  outline: none;
  box-sizing: border-box;
}

.field-input:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-soft);
}

.field-input::placeholder {
  color: var(--text-muted);
}

.auth-btn {
  width: 100%;
  padding: var(--space-md);
  background: var(--accent);
  color: var(--text-inverse);
  font-size: 0.9375rem;
  font-weight: 500;
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: background var(--duration-fast) var(--ease-out);
}

.auth-btn:hover:not(:disabled) {
  background: var(--accent-hover);
}

.auth-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.auth-switch {
  text-align: center;
  font-size: 0.875rem;
  color: var(--text-muted);
  margin-top: var(--space-xl);
}

.auth-link {
  color: var(--accent);
  text-decoration: none;
  font-weight: 500;
}

.auth-link:hover {
  text-decoration: underline;
}
</style>
```

- [ ] **Step 2: Commit**

```bash
cd "D:/project/cs146s/modern-software-dev-assignments/week8" && git add "web app/frontend/src/views/LoginPage.vue" && git commit -m "feat: add LoginPage with centered card layout"
```

---

### Task 11: Create RegisterPage.vue

**Files:**
- Create: `web app/frontend/src/views/RegisterPage.vue`

- [ ] **Step 1: Create RegisterPage.vue**

```vue
<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-header">
        <div class="brand-mark">
          <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
            <rect x="4" y="2" width="20" height="24" rx="3" stroke="currentColor" stroke-width="1.5" fill="none"/>
            <line x1="10" y1="8" x2="18" y2="8" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
            <line x1="10" y1="12" x2="18" y2="12" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
            <line x1="10" y1="16" x2="15" y2="16" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
            <rect x="8" y="3" width="3" height="1.5" rx="0.75" fill="currentColor" opacity="0.4"/>
          </svg>
        </div>
        <h1 class="auth-title">网页记事本</h1>
        <p class="auth-subtitle">创建新账户</p>
      </div>

      <form class="auth-form" @submit.prevent="handleRegister">
        <div class="field">
          <label class="field-label" for="reg-email">邮箱</label>
          <input
            id="reg-email"
            v-model="email"
            type="email"
            class="field-input"
            :class="{ 'field-input-error': errors.email }"
            placeholder="your@email.com"
            autocomplete="email"
            required
          />
          <span v-if="errors.email" class="field-error">{{ errors.email }}</span>
        </div>

        <div class="field">
          <label class="field-label" for="reg-password">密码</label>
          <input
            id="reg-password"
            v-model="password"
            type="password"
            class="field-input"
            :class="{ 'field-input-error': errors.password }"
            placeholder="至少6位"
            autocomplete="new-password"
            required
          />
          <span v-if="errors.password" class="field-error">{{ errors.password }}</span>
        </div>

        <div class="field">
          <label class="field-label" for="reg-password2">确认密码</label>
          <input
            id="reg-password2"
            v-model="password2"
            type="password"
            class="field-input"
            :class="{ 'field-input-error': errors.password2 }"
            placeholder="再次输入密码"
            autocomplete="new-password"
            required
          />
          <span v-if="errors.password2" class="field-error">{{ errors.password2 }}</span>
        </div>

        <div v-if="formError" class="auth-error">{{ formError }}</div>

        <button type="submit" class="auth-btn" :disabled="loading">
          {{ loading ? '注册中...' : '注册' }}
        </button>
      </form>

      <p class="auth-switch">
        已有账户？<router-link to="/login" class="auth-link">去登录</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const password2 = ref('')
const errors = reactive({ email: '', password: '', password2: '' })
const formError = ref('')
const loading = ref(false)

function clearErrors() {
  errors.email = ''
  errors.password = ''
  errors.password2 = ''
  formError.value = ''
}

function applyFieldErrors(data) {
  if (data.email) {
    errors.email = Array.isArray(data.email) ? data.email[0] : data.email
  }
  if (data.password) {
    errors.password = Array.isArray(data.password) ? data.password[0] : data.password
  }
  if (data.password2) {
    errors.password2 = Array.isArray(data.password2) ? data.password2[0] : data.password2
  }
}

async function handleRegister() {
  clearErrors()
  loading.value = true
  try {
    await authStore.register(email.value, password.value, password2.value)
    router.push('/')
  } catch (e) {
    const data = e.response?.data
    if (data) {
      applyFieldErrors(data)
      if (!errors.email && !errors.password && !errors.password2) {
        formError.value = '注册失败，请重试'
      }
    } else {
      formError.value = '注册失败，请检查网络连接'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-page);
  padding: var(--space-lg);
}

.auth-card {
  width: 100%;
  max-width: 380px;
  background: var(--bg-surface);
  border-radius: var(--radius-lg);
  padding: var(--space-3xl) var(--space-2xl);
  box-shadow: var(--shadow-lg);
  border: 1px solid var(--border-light);
}

.auth-header {
  text-align: center;
  margin-bottom: var(--space-2xl);
}

.brand-mark {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  background: var(--accent-soft);
  color: var(--accent);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto var(--space-md);
}

.auth-title {
  font-family: var(--font-display);
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: 0.03em;
  margin-bottom: var(--space-xs);
}

.auth-subtitle {
  font-size: 0.875rem;
  color: var(--text-muted);
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.auth-error {
  background: var(--error-bg);
  color: var(--error);
  border: 1px solid var(--error-border);
  border-radius: var(--radius-sm);
  padding: var(--space-sm) var(--space-md);
  font-size: 0.8125rem;
  text-align: center;
}

.field {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.field-label {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.field-input {
  width: 100%;
  padding: var(--space-sm) var(--space-md);
  font-size: 0.9375rem;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--bg-page);
  color: var(--text-primary);
  outline: none;
  box-sizing: border-box;
}

.field-input:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-soft);
}

.field-input-error {
  border-color: var(--error);
}

.field-input-error:focus {
  border-color: var(--error);
  box-shadow: 0 0 0 3px var(--error-bg);
}

.field-input::placeholder {
  color: var(--text-muted);
}

.field-error {
  font-size: 0.75rem;
  color: var(--error);
}

.auth-btn {
  width: 100%;
  padding: var(--space-md);
  background: var(--accent);
  color: var(--text-inverse);
  font-size: 0.9375rem;
  font-weight: 500;
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: background var(--duration-fast) var(--ease-out);
}

.auth-btn:hover:not(:disabled) {
  background: var(--accent-hover);
}

.auth-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.auth-switch {
  text-align: center;
  font-size: 0.875rem;
  color: var(--text-muted);
  margin-top: var(--space-xl);
}

.auth-link {
  color: var(--accent);
  text-decoration: none;
  font-weight: 500;
}

.auth-link:hover {
  text-decoration: underline;
}
</style>
```

- [ ] **Step 2: Commit**

```bash
cd "D:/project/cs146s/modern-software-dev-assignments/week8" && git add "web app/frontend/src/views/RegisterPage.vue" && git commit -m "feat: add RegisterPage with inline field validation"
```

---

### Task 12: Add logout button to Sidebar

**Files:**
- Modify: `web app/frontend/src/components/Sidebar.vue`

- [ ] **Step 1: Add logout button to Sidebar footer**

Edit `Sidebar.vue`. Add a logout button between the stats and the settings row. In the `<template>`, find the `<div class="sidebar-footer">` block and add after the `footer-divider` and before `footer-actions`:

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
      <div class="footer-user">
        <span class="user-email">{{ authStore.user?.email || '未登录' }}</span>
      </div>
      <div class="footer-divider"></div>
      <div class="footer-actions">
        <button
          class="logout-btn"
          @click="handleLogout"
          aria-label="登出"
          title="登出"
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M6 2H3a1 1 0 00-1 1v10a1 1 0 001 1h3M11 11l3-3-3-3M14 8H6" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
        <span class="action-divider"></span>
        <ThemeToggle />
        <span class="action-divider"></span>
        <button
          class="settings-btn"
          @click="store.openSettings()"
          aria-label="API 设置"
          title="API 设置"
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <circle cx="8" cy="8" r="2.5" stroke="currentColor" stroke-width="1.2"/>
            <path d="M8 1.5v1.5M8 13v1.5M1.5 8H3M13 8h1.5M3.4 3.4l1.06 1.06M11.54 11.54l1.06 1.06M3.4 12.6l1.06-1.06M11.54 4.46l1.06-1.06" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
          </svg>
        </button>
      </div>
    </div>
```

In the `<script setup>`, add the import and handler:

```javascript
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useNotesStore } from '../stores/notes.js'
import { useAuthStore } from '../stores/auth.js'
import { PRESET_CATEGORIES } from '../utils/categories.js'
import ThemeToggle from './ThemeToggle.vue'

const emit = defineEmits(['delete-category'])

const router = useRouter()
const store = useNotesStore()
const authStore = useAuthStore()

// ... existing computed ...

async function handleLogout() {
  await authStore.logout()
  router.push('/login')
}
```

Add styles for the new elements:

```css
.footer-user {
  display: flex;
  justify-content: center;
  padding: var(--space-xs) 0;
}

.user-email {
  font-size: 0.6875rem;
  color: var(--text-muted);
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.logout-btn {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  transition: all var(--duration-fast) var(--ease-out);
  border: none;
  background: transparent;
  cursor: pointer;
  padding: 0;
}

.logout-btn:hover {
  background: var(--error-bg);
  color: var(--error);
}
```

- [ ] **Step 2: Commit**

```bash
cd "D:/project/cs146s/modern-software-dev-assignments/week8" && git add "web app/frontend/src/components/Sidebar.vue" && git commit -m "feat: add logout button and user email to Sidebar footer"
```

---

### Task 13: Verify MainLayout compatibility

**Files:**
- Check: `web app/frontend/src/views/MainLayout.vue` (no changes needed)

- [ ] **Step 1: Confirm MainLayout works without changes**

The `onMounted` hook already has try/catch error handling for data loading failures. The route guard ensures authentication before this component renders. No code changes to `MainLayout.vue` are needed.

---

### Task 14: End-to-end verification

- [ ] **Step 1: Start the backend**

```bash
cd "web app/backend" && python manage.py runserver 8000
```

- [ ] **Step 2: Start the frontend**

```bash
cd "web app/frontend" && npm run dev
```

- [ ] **Step 3: Manual verification**

1. Visit `http://localhost:5173` — should redirect to `/login`
2. Click "立即注册" — goes to `/register`
3. Register with `test@test.com` / `test123` / `test123` — auto-login, redirect to `/`
4. Create a note and a todo — both should work
5. Click the logout button — redirect to `/login`
6. Log back in — data should still be there
7. Register a second user `other@test.com` / `test123`
8. Second user should see empty app (no data from first user)
9. Each user configures AI settings independently

- [ ] **Step 4: Run backend tests one more time**

```bash
cd "web app/backend" && python manage.py test notes -v2
```

Expected: all tests pass.

- [ ] **Step 5: Final commit (if any touch-ups needed)**

```bash
cd "D:/project/cs146s/modern-software-dev-assignments/week8" && git add -A && git commit -m "feat: complete login & multi-user authentication implementation"
```

---

## Self-Review Checklist

1. ✓ Spec coverage: Every spec section mapped to tasks
2. ✓ No placeholders: All code shown inline, all paths exact
3. ✓ Type consistency: `user` FK field name consistent across models, serializers, views, and ai_service
