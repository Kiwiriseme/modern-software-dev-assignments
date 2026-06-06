# Login & Multi-User Authentication — Design Spec

**Date:** 2026-06-06
**Branch:** `lqy_week8`
**Status:** approved

## Overview

Add multi-user authentication (open registration + login via Django session) to the existing Django DRF + Vue.js note/todo management app. Each user gets isolated data and their own AI settings. No quotas in this phase.

## Architecture

```
Browser (LoginPage/RegisterPage) → Axios → Django Session → DRF ViewSet → SQLite
                                          ↕
                              Django auth.User (built-in)
```

- **Authentication:** Django session-based (cookie). No JWT.
- **User model:** `django.contrib.auth.models.User` (no custom model).
- **Registration:** open, no email verification or admin approval required.

## Data Model Changes

### User — reused from Django built-in

`django.contrib.auth.models.User` provides `username`, `email`, `password`, `is_active`, etc. We use `email` as the login identifier (also stored in `username` for simplicity).

### Model changes in `notes/models.py`

**Todo:**
- Add `user = ForeignKey(User, on_delete=CASCADE, related_name="todos")` — NOT NULL, set on create

**Note:**
- Add `user = ForeignKey(User, on_delete=CASCADE, related_name="notes")` — NOT NULL, set on create

**AISettings:**
- Replace singleton pattern (`pk=1`, `get_solo()`) with per-user
- Add `user = OneToOneField(User, on_delete=CASCADE, related_name="ai_settings")`
- Remove `get_solo()` classmethod
- Add `get_for_user(user)` or use `user.ai_settings` directly

**Migration strategy:** One new migration (`0004_add_user_fk.py`). For existing data, create a default admin user (`admin@admin.com` / `admin123`) and assign all existing records to that user so existing data is not lost. The admin user password is printed to console during migration.

## API Design

### New Endpoints

| Method | URL | Auth | Request Body | Response | Status Codes |
|--------|-----|------|-------------|----------|--------------|
| `POST` | `/api/v1/auth/register` | No | `{email, password, password2}` | User info | 201 / 400 |
| `POST` | `/api/v1/auth/login` | No | `{email, password}` | User info | 200 / 401 |
| `POST` | `/api/v1/auth/logout` | Yes | — | `{detail: "已登出"}` | 200 |
| `GET` | `/api/v1/auth/me` | Yes | — | `{id, email}` | 200 / 401 |

### Existing Endpoint Changes

- All CRUD (notes, todos, categories): add `permission_classes = [IsAuthenticated]`
- QuerySet filtering: filter by `request.user` — e.g., `Todo.objects.filter(user=request.user)`
- `GET/PUT /api/v1/ai-settings/1` → `GET/PUT /api/v1/ai-settings` (no PK needed; backend resolves `request.user.ai_settings`)
- `api/ai-settings` action in frontend drops the `/1`

### Registration Logic

1. Validate email format (basic regex)
2. Validate password ≥ 6 characters
3. Validate `password == password2`
4. Check email uniqueness
5. Create `User(username=email, email=email)` then `user.set_password(password)`
6. Create `AISettings(user=user)` with defaults
7. Log user in (`django.contrib.auth.login(request, user)`)
8. Return 201 with user info

### Login Logic

1. Find user by `email`
2. Authenticate with `django.contrib.auth.authenticate(username=email, password=password)`
3. If success: `login(request, user)`, return 200
4. If fail: return 401 `{"detail": "邮箱或密码错误"}`

### Logout Logic

1. `django.contrib.auth.logout(request)`
2. Return 200

## Error Handling

### Registration Errors (400)

| Field | Condition | Message |
|-------|-----------|---------|
| `email` | Invalid format | "邮箱格式不正确" |
| `email` | Already exists | "该邮箱已被注册" |
| `password` | Length < 6 | "密码至少6位" |
| `password2` | != password | "两次密码不一致" |

### Login Errors (401)

| Condition | Message |
|-----------|---------|
| Wrong email or password | "邮箱或密码错误" |

### Auth Guard (401)

- Frontend axios response interceptor: on 401, redirect to `/login`
- Backend DRF: `IsAuthenticated` → 401 for unauthenticated requests

### Data Isolation

- Queryset always filtered by `request.user`
- Attempting to access another user's resource returns 404 (not 403), to avoid exposing resource existence

## Frontend Changes

### New Routes (`src/router/index.js`)

```js
{ path: '/login', name: 'login', component: () => import('../views/LoginPage.vue') },
{ path: '/register', name: 'register', component: () => import('../views/RegisterPage.vue') },
```

### New Route Guard

```js
router.beforeEach(async (to, from, next) => {
  if (to.name === 'login' || to.name === 'register') {
    // If already logged in, redirect to home
    const loggedIn = await checkAuth() // calls GET /api/v1/auth/me
    if (loggedIn) return next('/')
    return next()
  }
  // Protected routes
  const loggedIn = await checkAuth()
  if (!loggedIn) return next('/login')
  next()
})
```

### New Components

**LoginPage.vue:**
- Centered card layout matching app aesthetic
- Email input, password input, submit button
- Link to register page: "还没有账户？立即注册"
- Error display (form-level for auth failure)

**RegisterPage.vue:**
- Centered card layout
- Email, password, confirm password inputs
- Validation feedback inline below each field
- Link to login: "已有账户？去登录"
- On success: auto-login, redirect to `/`

### Modified Components

**Sidebar.vue:**
- Add "登出" button in footer area (alongside existing gear icon)
- On click: call logout API, redirect to `/login`

**MainLayout.vue:**
- Accept current user info from store for display

### New Store (`src/stores/auth.js` or extend notes.js)

- `user: ref(null)` — current user object
- `isAuthenticated: computed(() => !!user.value)`
- `fetchUser()` — GET `/auth/me`
- `login(email, password)` — POST `/auth/login`
- `register(email, password, password2)` — POST `/auth/register`
- `logout()` — POST `/auth/logout`

### API Additions (`src/api/index.js`)

```js
export function register(data)    { return api.post('/auth/register', data) }
export function login(data)       { return api.post('/auth/login', data) }
export function logout()          { return api.post('/auth/logout') }
export function fetchCurrentUser(){ return api.get('/auth/me') }
```

Add response interceptor:
```js
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      router.push('/login')
    }
    return Promise.reject(error)
  }
)
```

Update `fetchAISettings()` and `saveAISettings()` to remove hardcoded `/1` path.

## Test Plan

### Backend Tests (added to `notes/tests.py`)

| # | Test | Expected |
|---|------|----------|
| 1 | Register with valid data | 201, user created, session set |
| 2 | Register with duplicate email | 400, "该邮箱已被注册" |
| 3 | Register with short password | 400, "密码至少6位" |
| 4 | Register with mismatched passwords | 400, "两次密码不一致" |
| 5 | Register with invalid email | 400 |
| 6 | Login with correct credentials | 200, session set |
| 7 | Login with wrong password | 401, "邮箱或密码错误" |
| 8 | Login with non-existent email | 401 |
| 9 | Logout | 200, session cleared |
| 10 | GET /auth/me when logged in | 200, returns user info |
| 11 | GET /auth/me when not logged in | 401 |
| 12 | CRUD todos without auth | 401 |
| 13 | CRUD notes without auth | 401 |
| 14 | User A cannot see User B's notes | 404 |
| 15 | User A cannot see User B's todos | 404 |
| 16 | User A's AI settings isolated from User B | verified |
| 17 | GET/PUT /ai-settings returns current user's config | 200 |

### Frontend Tests (manual or lightweight)

- Visit `/` when not logged in → redirected to `/login`
- Visit `/login` when logged in → redirected to `/`
- Register → auto-login → redirected to `/`
- Login → redirected to `/`
- Logout → redirected to `/login`

## Files Affected

### Backend (Django)

| File | Change |
|------|--------|
| `notes/models.py` | Add `user` FK to Note/Todo; `user` OneToOne to AISettings |
| `notes/serializers.py` | Add RegisterSerializer, LoginSerializer; update AISettingsSerializer |
| `notes/views.py` | Add AuthViewSet; add `permission_classes` + user filtering to all viewsets |
| `notes/urls.py` | Register `/auth/` routes |
| `notes/tests.py` | Add auth + isolation tests |
| `notes/migrations/0004_*.py` | New migration (auto-generated + data migration for existing records) |

### Frontend (Vue.js)

| File | Change |
|------|--------|
| `src/router/index.js` | Add `/login`, `/register` routes + beforeEach guard |
| `src/api/index.js` | Add auth API functions + 401 interceptor; update AI settings path |
| `src/stores/auth.js` | **New** — user auth state store |
| `src/views/LoginPage.vue` | **New** — login form |
| `src/views/RegisterPage.vue` | **New** — registration form |
| `src/components/Sidebar.vue` | Add logout button in footer |
| `src/views/MainLayout.vue` | Minor adjustments for auth awareness |

## Out of Scope

- Email verification / password reset
- AI usage quotas or rate limiting
- User roles / permissions system
- Password strength beyond 6-char minimum
- Social login (OAuth)
- Account deletion by user
