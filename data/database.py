"""
Database layer: SQLite-based job cache.
Uses parameterized queries throughout — no string interpolation in SQL.
"""

import logging
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, Generator, List, Optional

logger = logging.getLogger(__name__)

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    company TEXT,
    location TEXT,
    description TEXT,
    url TEXT,
    salary_min REAL,
    salary_max REAL,
    created TEXT,
    contract_type TEXT,
    source TEXT,
    cached_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_jobs_title ON jobs (title);
CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs (company);
CREATE INDEX IF NOT EXISTS idx_jobs_location ON jobs (location);
"""


class JobDatabase:
    def __init__(self, db_path: str = "data/nexthire.db") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    @contextmanager
    def _connect(self) -> Generator[sqlite3.Connection, None, None]:
        conn = sqlite3.connect(self.db_path, timeout=10)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(SCHEMA_SQL)

    def upsert_jobs(self, jobs: List[Dict]) -> int:
        """Insert or replace jobs. Returns count of upserted rows."""
        if not jobs:
            return 0

        sql = """
            INSERT OR REPLACE INTO jobs
                (id, title, company, location, description, url,
                 salary_min, salary_max, created, contract_type, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        rows = [
            (
                j.get("id", ""),
                j.get("title", ""),
                j.get("company", ""),
                j.get("location", ""),
                j.get("description", ""),
                j.get("url", ""),
                j.get("salary_min"),
                j.get("salary_max"),
                j.get("created"),
                j.get("contract_type", ""),
                j.get("source", ""),
            )
            for j in jobs
            if j.get("id")  # skip jobs without an ID
        ]

        with self._connect() as conn:
            conn.executemany(sql, rows)
        return len(rows)

    def search_jobs(
        self,
        query: str,
        location: str = "",
        limit: int = 20,
    ) -> List[Dict]:
        """
        Full-text-style search over title + description.
        Uses LIKE with parameterized values — safe from SQL injection.
        """
        terms = f"%{query}%"
        loc_terms = f"%{location}%" if location else "%"

        sql = """
            SELECT * FROM jobs
            WHERE (title LIKE ? OR description LIKE ?)
              AND (location LIKE ? OR ? = '%')
            ORDER BY cached_at DESC
            LIMIT ?
        """
        with self._connect() as conn:
            rows = conn.execute(sql, (terms, terms, loc_terms, loc_terms, limit)).fetchall()
        return [dict(row) for row in rows]

    def get_job_count(self) -> int:
        with self._connect() as conn:
            return conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]

    def purge_old_jobs(self, days: int = 30) -> int:
        """Remove jobs cached more than `days` ago."""
        sql = "DELETE FROM jobs WHERE cached_at < datetime('now', ?)"
        with self._connect() as conn:
            cursor = conn.execute(sql, (f"-{days} days",))
        return cursor.rowcount
