# Action Item Extractor

A FastAPI-based web application that extracts actionable tasks from meeting notes or free-form text. It supports two extraction strategies: a lightweight rule-based parser and an LLM-powered extractor via Ollama. Extracted items are persisted in SQLite and surfaced through a RESTful API and a minimal vanilla-HTML frontend.

## Quickstart

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com/) installed and running (required for LLM-based extraction)
- Pull the LLM model used by the project:

```bash
ollama pull mistral-nemo:12b
```

### Setup

1. Clone the repository and navigate to the project root:

```bash
cd modern-software-dev-assignments
```

2. Create and activate a virtual environment, then install dependencies with Poetry:

```bash
conda create -n cs146s python=3.12 -y
conda activate cs146s
poetry install --no-interaction
```

3. (Optional) Create a `.env` file in `week2/` to override default settings. Supported variables:

```
LLM_MODEL=mistral-nemo:12b
DB_NAME=app.db
```

### Run the Application

From the repository root, start the FastAPI server in development mode:

```bash
uvicorn week2.app.main:app --reload --port 8000
```

Then open:

- Frontend: [http://localhost:8000](http://localhost:8000)
- Interactive API docs (Swagger UI): [http://localhost:8000/docs](http://localhost:8000/docs)

## Project Structure

```
week2/
├── app/
│   ├── routers/
│   │   ├── action_items.py    # Action item extraction & management endpoints
│   │   └── notes.py           # Note CRUD endpoints
│   ├── services/
│   │   └── extract.py         # Rule-based & LLM action item extraction logic
│   ├── config.py              # Centralized settings (env, paths, model)
│   ├── db.py                  # SQLite database layer (raw sqlite3)
│   ├── main.py                # FastAPI app entry point & lifespan
│   └── schemas.py             # Pydantic request/response models
├── frontend/
│   └── index.html             # Vanilla HTML/JS single-page UI
├── tests/
│   └── test_extract.py        # Unit tests for extraction logic
└── data/                      # Auto-created; holds SQLite database
```

## API Endpoints

All endpoints are served under `http://localhost:8000`.

### Notes

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/notes` | Create a new note. Request body: `{"content": "..."}`. Returns the created note with `id` and `created_at`. |
| `GET` | `/notes` | List all notes, ordered by most recent first. |
| `GET` | `/notes/{note_id}` | Retrieve a single note by its ID. Returns `404` if not found. |

### Action Items

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/action-items/extract` | Extract action items using rule-based parser. Request body: `{"text": "...", "save_note": false}`. If `save_note` is `true`, the input text is also persisted as a note. |
| `POST` | `/action-items/extract-llm` | Extract action items using Ollama LLM. Same request format as above. Requires Ollama to be running locally. |
| `GET` | `/action-items` | List all action items. Optional query parameter `?note_id=<id>` filters by associated note. |
| `POST` | `/action-items/{action_item_id}/done` | Mark an action item as done or undone. Request body: `{"done": true}` (or `false`). |

### Root

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Serves the frontend HTML page (Action Item Extractor UI). |

### Request/Response Schemas

**POST `/notes` — Request**
```json
{
  "content": "Meeting notes: set up database, write tests, update docs"
}
```

**POST `/action-items/extract` (and `/extract-llm`) — Request**
```json
{
  "text": "- [ ] Set up database\n- Write tests\n* Update docs",
  "save_note": true
}
```

**Extraction Response**
```json
{
  "note_id": 1,
  "items": [
    { "id": 1, "text": "Set up database" },
    { "id": 2, "text": "Write tests" },
    { "id": 3, "text": "Update docs" }
  ]
}
```

## Tests

The project uses **pytest** for unit testing. All tests are located in `week2/tests/`.

### Run Tests

From the repository root:

```bash
pytest week2/tests/ -v
```

Or from within the `week2/` directory:

```bash
cd week2 && pytest tests/ -v
```

### Test Coverage

The test suite covers the extraction service (`test_extract.py`):

- **Rule-based extraction** — verifies bullet lists (`-`, `*`, `1.`), checkbox markers (`[ ]`), and narrative fallback are handled correctly.
- **LLM-based extraction** — uses `unittest.mock` to patch the Ollama `chat` call and validates:
  - Bullet list input parsing
  - Keyword-prefixed lines (`TODO:`, `action:`, `next:`)
  - Plain paragraph text extraction
  - Empty and whitespace-only input boundaries
  - Case-insensitive deduplication
  - Whitespace trimming on returned items
  - Empty item filtering from LLM responses
  - Mix of checkboxes, keywords, and narrative text
  - Correct model name and structured output format passed to `chat()`

### Write New Tests

Add test files under `week2/tests/` with filenames matching `test_*.py`. Follow the existing pattern of patching external dependencies and asserting on return values.
