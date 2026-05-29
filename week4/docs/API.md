# API Reference

Base URL: `http://localhost:8000`

## Notes

| Method | Path               | Description        | Request Body                                              | Response         |
| ------ | ------------------ | ------------------ | --------------------------------------------------------- | ---------------- |
| GET    | `/notes/`          | List all notes     | -                                                         | `[NoteRead]`     |
| POST   | `/notes/`          | Create a note      | `{"title": str, "content": str}`                          | `NoteRead` (201) |
| GET    | `/notes/search/`   | Search notes       | Query: `?q=<term>` (case-insensitive, matches title+body) | `[NoteRead]`     |
| GET    | `/notes/{id}`      | Get note by ID     | -                                                         | `NoteRead`       |
| PUT    | `/notes/{id}`      | Update a note      | `{"title"?: str, "content"?: str}` (partial update ok)    | `NoteRead`       |
| DELETE | `/notes/{id}`      | Delete a note      | -                                                         | 204 No Content   |

### NoteRead schema

```json
{
  "id": 1,
  "title": "My Note",
  "content": "Note content here"
}
```

### Validation rules

- `title`: required, 1-200 characters
- `content`: required, at least 1 character
- Returns 422 for validation failures, 404 for missing resources

## Action Items

| Method | Path                          | Description              | Request Body                   | Response             |
| ------ | ----------------------------- | ------------------------ | ------------------------------ | -------------------- |
| GET    | `/action-items/`              | List all action items    | -                              | `[ActionItemRead]`   |
| POST   | `/action-items/`              | Create an action item    | `{"description": str}`         | `ActionItemRead`(201)|
| PUT    | `/action-items/{id}/complete` | Mark item as completed   | -                              | `ActionItemRead`     |

### ActionItemRead schema

```json
{
  "id": 1,
  "description": "Write tests",
  "completed": false
}
```

## Services

### Extraction (`backend/app/services/extract.py`)

- `extract_action_items(text: str) -> list[str]` — extracts TODO lines and lines ending with `!`
- `extract_tags(text: str) -> list[str]` — extracts `#tag` patterns from text
