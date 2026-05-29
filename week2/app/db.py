from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager

from .config import get_settings

_SETTINGS = get_settings()

SQL_CREATE_NOTES = """
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now'))
);
"""

SQL_CREATE_ACTION_ITEMS = """
CREATE TABLE IF NOT EXISTS action_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    note_id INTEGER,
    text TEXT NOT NULL,
    done INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (note_id) REFERENCES notes(id)
);
"""


def init_db() -> None:
    _SETTINGS.DATA_DIR.mkdir(parents=True, exist_ok=True)
    with _get_connection() as conn:
        conn.execute(SQL_CREATE_NOTES)
        conn.execute(SQL_CREATE_ACTION_ITEMS)
        conn.commit()


@contextmanager
def _get_connection() -> Iterator[sqlite3.Connection]:
    _SETTINGS.DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(_SETTINGS.DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def insert_note(content: str) -> int:
    with _get_connection() as conn:
        cursor = conn.execute("INSERT INTO notes (content) VALUES (?)", (content,))
        conn.commit()
        return int(cursor.lastrowid)


def list_notes() -> list[sqlite3.Row]:
    with _get_connection() as conn:
        rows = conn.execute("SELECT id, content, created_at FROM notes ORDER BY id DESC")
        return list(rows.fetchall())


def get_note(note_id: int) -> sqlite3.Row | None:
    with _get_connection() as conn:
        row = conn.execute(
            "SELECT id, content, created_at FROM notes WHERE id = ?",
            (note_id,),
        ).fetchone()
        return row


def insert_action_items(items: list[str], note_id: int | None = None) -> list[int]:
    with _get_connection() as conn:
        ids: list[int] = []
        for item in items:
            cursor = conn.execute(
                "INSERT INTO action_items (note_id, text) VALUES (?, ?)",
                (note_id, item),
            )
            ids.append(int(cursor.lastrowid))
        conn.commit()
        return ids


def list_action_items(note_id: int | None = None) -> list[sqlite3.Row]:
    with _get_connection() as conn:
        if note_id is None:
            rows = conn.execute(
                "SELECT id, note_id, text, done, created_at FROM action_items ORDER BY id DESC"
            )
        else:
            rows = conn.execute(
                "SELECT id, note_id, text, done, created_at FROM action_items "
                "WHERE note_id = ? ORDER BY id DESC",
                (note_id,),
            )
        return list(rows.fetchall())


def mark_action_item_done(action_item_id: int, done: bool) -> None:
    with _get_connection() as conn:
        conn.execute(
            "UPDATE action_items SET done = ? WHERE id = ?",
            (1 if done else 0, action_item_id),
        )
        conn.commit()
