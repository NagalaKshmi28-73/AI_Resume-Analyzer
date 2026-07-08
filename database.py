"""
Lightweight SQLite persistence for analysis history.
"""
import sqlite3
import json
import os
from datetime import datetime
import config


def _get_connection():
    os.makedirs(os.path.dirname(config.DB_PATH) or ".", exist_ok=True)
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = _get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS analysis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            job_role TEXT NOT NULL,
            ats_score REAL NOT NULL,
            match_score REAL NOT NULL,
            skills_found TEXT,
            missing_required TEXT,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def save_analysis(filename: str, job_role: str, ats_score: float, match_score: float,
                   skills_found: list, missing_required: list) -> int:
    conn = _get_connection()
    cursor = conn.execute(
        """
        INSERT INTO analysis_history
            (filename, job_role, ats_score, match_score, skills_found, missing_required, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            filename,
            job_role,
            ats_score,
            match_score,
            json.dumps(skills_found),
            json.dumps(missing_required),
            datetime.utcnow().isoformat(),
        ),
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id


def get_history(limit: int = 20) -> list[dict]:
    conn = _get_connection()
    rows = conn.execute(
        "SELECT * FROM analysis_history ORDER BY created_at DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def clear_history():
    conn = _get_connection()
    conn.execute("DELETE FROM analysis_history")
    conn.commit()
    conn.close()
