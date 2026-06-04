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
