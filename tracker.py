"""SQLite-backed job application tracker (stdlib only, no extra dependencies)."""

from __future__ import annotations

import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import date, datetime
from pathlib import Path

STATUSES = ["Saved", "Applied", "Interview", "Offer", "Rejected"]
DEFAULT_DB = Path(os.environ.get("SKILLMATCH_DB", Path(__file__).parent / "data" / "skillmatch.db"))

_SCHEMA = """
CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company TEXT NOT NULL,
    role TEXT NOT NULL,
    url TEXT DEFAULT '',
    status TEXT NOT NULL DEFAULT 'Saved',
    applied_date TEXT,
    notes TEXT DEFAULT '',
    job_description TEXT DEFAULT '',
    score INTEGER,
    evidence_score INTEGER,
    missing TEXT DEFAULT '[]',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
)
"""

_UPDATABLE = {
    "company", "role", "url", "status", "applied_date", "notes",
    "job_description", "score", "evidence_score", "missing",
}


@contextmanager
def _connect(db_path=None):
    path = Path(db_path or DEFAULT_DB)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute(_SCHEMA)
        yield conn
        conn.commit()
    finally:
        conn.close()


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _row_to_dict(row: sqlite3.Row) -> dict:
    data = dict(row)
    try:
        data["missing"] = json.loads(data.get("missing") or "[]")
    except json.JSONDecodeError:
        data["missing"] = []
    return data


def add_application(
    company: str,
    role: str,
    url: str = "",
    status: str = "Saved",
    applied_date: str | None = None,
    notes: str = "",
    job_description: str = "",
    score: int | None = None,
    evidence_score: int | None = None,
    missing: list[str] | None = None,
    db_path=None,
) -> int:
    company, role = company.strip(), role.strip()
    if not company or not role:
        raise ValueError("Company and role are required.")
    if status not in STATUSES:
        raise ValueError(f"Unknown status: {status}")
    if applied_date is None and status != "Saved":
        applied_date = date.today().isoformat()

    now = _now()
    with _connect(db_path) as conn:
        cur = conn.execute(
            """INSERT INTO applications
               (company, role, url, status, applied_date, notes, job_description,
                score, evidence_score, missing, created_at, updated_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            (company, role, url.strip(), status, applied_date, notes,
             job_description, score, evidence_score,
             json.dumps(missing or []), now, now),
        )
        return cur.lastrowid


def get_application(app_id: int, db_path=None) -> dict | None:
    with _connect(db_path) as conn:
        row = conn.execute("SELECT * FROM applications WHERE id = ?", (app_id,)).fetchone()
    return _row_to_dict(row) if row else None


def list_applications(status: str | None = None, db_path=None) -> list[dict]:
    query = "SELECT * FROM applications"
    params: tuple = ()
    if status:
        query += " WHERE status = ?"
        params = (status,)
    query += " ORDER BY updated_at DESC, id DESC"
    with _connect(db_path) as conn:
        rows = conn.execute(query, params).fetchall()
    return [_row_to_dict(r) for r in rows]


def update_application(app_id: int, db_path=None, **fields) -> None:
    unknown = set(fields) - _UPDATABLE
    if unknown:
        raise ValueError(f"Cannot update fields: {', '.join(sorted(unknown))}")
    if "status" in fields and fields["status"] not in STATUSES:
        raise ValueError(f"Unknown status: {fields['status']}")
    if "missing" in fields and not isinstance(fields["missing"], str):
        fields["missing"] = json.dumps(fields["missing"] or [])

    current = get_application(app_id, db_path)
    if current is None:
        raise ValueError(f"No application with id {app_id}.")
    if fields.get("status", "Saved") != "Saved" and not (
        current["applied_date"] or fields.get("applied_date")
    ):
        fields["applied_date"] = date.today().isoformat()

    fields["updated_at"] = _now()
    assignments = ", ".join(f"{name} = ?" for name in fields)  # names are whitelisted above
    with _connect(db_path) as conn:
        conn.execute(
            f"UPDATE applications SET {assignments} WHERE id = ?",
            (*fields.values(), app_id),
        )


def delete_application(app_id: int, db_path=None) -> None:
    with _connect(db_path) as conn:
        conn.execute("DELETE FROM applications WHERE id = ?", (app_id,))


def status_counts(db_path=None) -> dict[str, int]:
    counts = {s: 0 for s in STATUSES}
    with _connect(db_path) as conn:
        for row in conn.execute("SELECT status, COUNT(*) AS n FROM applications GROUP BY status"):
            counts[row["status"]] = row["n"]
    return counts


def score_insights(db_path=None) -> dict | None:
    """Average match score for jobs that progressed vs. ones that were rejected."""
    def avg(statuses):
        marks = ",".join("?" for _ in statuses)
        with _connect(db_path) as conn:
            row = conn.execute(
                f"SELECT AVG(score) AS a, COUNT(score) AS n FROM applications "
                f"WHERE score IS NOT NULL AND status IN ({marks})",
                statuses,
            ).fetchone()
        return row["a"], row["n"]

    advanced_avg, advanced_n = avg(["Interview", "Offer"])
    rejected_avg, rejected_n = avg(["Rejected"])
    if not advanced_n or not rejected_n:
        return None
    return {
        "advanced_avg": round(advanced_avg),
        "advanced_n": advanced_n,
        "rejected_avg": round(rejected_avg),
        "rejected_n": rejected_n,
    }
