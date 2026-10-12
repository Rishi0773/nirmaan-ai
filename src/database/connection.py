"""
NIRMAAN AI - SQLite Database Connection Manager
Provides thread-safe connections, initialization, and transactional safety.
"""

import sqlite3
from pathlib import Path
from src.config import DB_PATH

SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"


def get_connection(db_path=DB_PATH) -> sqlite3.Connection:
    """Returns a SQLite connection with dict-like row access and WAL mode."""
    conn = sqlite3.connect(db_path, timeout=15.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    return conn


def init_db(db_path=DB_PATH):
    """Initializes the database schema if tables do not exist."""
    conn = get_connection(db_path)
    with conn:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
    conn.close()


def reset_db(db_path=DB_PATH):
    """Safely drops and recreates tables for development/testing."""
    conn = get_connection(db_path)
    with conn:
        tables = [
            "audit_logs", "notifications", "cleanup_verifications", "cleanup_tasks",
            "priority_scores", "hotspot_reports", "hotspots", "severity_assessments",
            "detections", "report_images", "reports", "users"
        ]
        for t in tables:
            conn.execute(f"DROP TABLE IF EXISTS {t};")
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
    conn.close()


if __name__ == "__main__":
    init_db()
    print(f"NIRMAAN AI Database successfully initialized at {DB_PATH}")
