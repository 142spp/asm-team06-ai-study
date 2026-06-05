import json
import sqlite3
from pathlib import Path
from typing import Any

_DB_PATH = Path(__file__).parent.parent.parent / "preferences.db"


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(_DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS preferences (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            original   TEXT NOT NULL,
            modified   TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """
    )
    conn.commit()
    return conn


def load_preferences() -> list[dict[str, Any]]:
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT original, modified FROM preferences ORDER BY id"
        ).fetchall()
    return [
        {"original": json.loads(row[0]), "modified": json.loads(row[1])}
        for row in rows
    ]


def save_preference(original: dict[str, Any], modified: dict[str, Any]) -> None:
    with _get_conn() as conn:
        conn.execute(
            "INSERT INTO preferences (original, modified) VALUES (?, ?)",
            (json.dumps(original, ensure_ascii=False), json.dumps(modified, ensure_ascii=False)),
        )
