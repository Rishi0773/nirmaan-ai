"""
NIRMAAN AI - SQLite Database Connection Manager
Provides thread-safe connections, initialization, backward-compatible migrations,
and transactional safety with WAL mode.
"""

import sqlite3
from pathlib import Path
from src.config import DB_PATH

SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"


def apply_migrations(conn: sqlite3.Connection):
    """
    Applies non-destructive schema migrations:
    - Expands lifecycle status CHECK constraints on reports and cleanup_tasks
    - Adds citizen_id, duplicate_of_id, rejection_reason, worker_id, etc.
    - Creates report_status_history and report_followups tables
    - Creates performance indexes
    Preserves 100% of existing rows and relational integrity.
    """
    conn.execute("PRAGMA foreign_keys = OFF;")

    def _copy_table_data(src_table, dst_table):
        src_cols = [r[1] for r in conn.execute(f"PRAGMA table_info({src_table})").fetchall()]
        dst_cols = [r[1] for r in conn.execute(f"PRAGMA table_info({dst_table})").fetchall()]
        common_cols = [c for c in src_cols if c in dst_cols]
        cols_str = ", ".join(common_cols)
        conn.execute(f"INSERT INTO {dst_table} ({cols_str}) SELECT {cols_str} FROM {src_table};")

    # 1. Ensure report_status_history table exists
    conn.execute("""
    CREATE TABLE IF NOT EXISTS report_status_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        report_id INTEGER NOT NULL,
        old_status TEXT,
        new_status TEXT NOT NULL,
        changed_by_user_id INTEGER,
        changed_by_name TEXT,
        reason TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(report_id) REFERENCES reports(id) ON DELETE CASCADE,
        FOREIGN KEY(changed_by_user_id) REFERENCES users(id) ON DELETE SET NULL
    );
    """)

    # 2. Ensure report_followups table exists
    conn.execute("""
    CREATE TABLE IF NOT EXISTS report_followups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        report_id INTEGER NOT NULL,
        user_id INTEGER,
        user_name TEXT,
        notes TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(report_id) REFERENCES reports(id) ON DELETE CASCADE,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE SET NULL
    );
    """)

    # 3. Check reports table CHECK constraint
    rep_row = conn.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='reports'").fetchone()
    if rep_row:
        sql = rep_row[0]
        if "Verified Closed" not in sql or "Awaiting Verification" not in sql or "In Progress" not in sql:
            with conn:
                conn.execute("""
                CREATE TABLE reports_migrated (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    report_uid TEXT UNIQUE NOT NULL,
                    latitude REAL NOT NULL,
                    longitude REAL NOT NULL,
                    address TEXT,
                    ward_name TEXT NOT NULL,
                    landmark TEXT,
                    description TEXT,
                    waste_category TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'Pending' CHECK(status IN (
                        'Pending', 'Submitted', 'Under Review', 'Prioritized', 'Assigned',
                        'In Progress', 'Under Cleanup', 'Awaiting Verification', 'Cleared',
                        'Verified Closed', 'Blocked', 'Rejected', 'Duplicate', 'Reopened'
                    )),
                    reporter_name TEXT DEFAULT 'Anonymous Citizen',
                    reporter_contact TEXT,
                    citizen_id INTEGER,
                    duplicate_of_id INTEGER,
                    rejection_reason TEXT,
                    blocked_reason TEXT,
                    escalated INTEGER DEFAULT 0,
                    escalation_notes TEXT,
                    is_simulated INTEGER DEFAULT 0,
                    is_flagged INTEGER DEFAULT 0,
                    flag_reason TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(citizen_id) REFERENCES users(id) ON DELETE SET NULL,
                    FOREIGN KEY(duplicate_of_id) REFERENCES reports(id) ON DELETE SET NULL
                );
                """)
                _copy_table_data("reports", "reports_migrated")
                conn.execute("DROP TABLE reports;")
                conn.execute("ALTER TABLE reports_migrated RENAME TO reports;")

    # 4. Check cleanup_tasks table CHECK constraint
    tasks_row = conn.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='cleanup_tasks'").fetchone()
    if tasks_row:
        sql = tasks_row[0]
        if "Awaiting Verification" not in sql or "In Progress" not in sql or "Blocked" not in sql:
            with conn:
                conn.execute("""
                CREATE TABLE cleanup_tasks_migrated (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_code TEXT UNIQUE NOT NULL,
                    report_id INTEGER NOT NULL UNIQUE,
                    assigned_team TEXT NOT NULL,
                    supervisor_id INTEGER,
                    worker_id INTEGER,
                    status TEXT NOT NULL DEFAULT 'Pending' CHECK(status IN (
                        'Pending', 'Assigned', 'In Progress', 'Under Cleanup', 'Blocked',
                        'Awaiting Verification', 'Cleared', 'Verified Closed', 'Reopened'
                    )),
                    priority_level TEXT DEFAULT 'Normal',
                    scheduled_at TIMESTAMP,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    notes TEXT,
                    worker_notes TEXT,
                    blocked_reason TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(report_id) REFERENCES reports(id) ON DELETE CASCADE,
                    FOREIGN KEY(supervisor_id) REFERENCES users(id) ON DELETE SET NULL,
                    FOREIGN KEY(worker_id) REFERENCES users(id) ON DELETE SET NULL
                );
                """)
                _copy_table_data("cleanup_tasks", "cleanup_tasks_migrated")
                conn.execute("DROP TABLE cleanup_tasks;")
                conn.execute("ALTER TABLE cleanup_tasks_migrated RENAME TO cleanup_tasks;")

    # 5. Add any missing columns to reports safely
    if conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='reports'").fetchone():
        cols_reports = [r[1] for r in conn.execute("PRAGMA table_info(reports)").fetchall()]
        if "citizen_id" not in cols_reports:
            conn.execute("ALTER TABLE reports ADD COLUMN citizen_id INTEGER;")
        if "duplicate_of_id" not in cols_reports:
            conn.execute("ALTER TABLE reports ADD COLUMN duplicate_of_id INTEGER;")
        if "rejection_reason" not in cols_reports:
            conn.execute("ALTER TABLE reports ADD COLUMN rejection_reason TEXT;")
        if "blocked_reason" not in cols_reports:
            conn.execute("ALTER TABLE reports ADD COLUMN blocked_reason TEXT;")
        if "escalated" not in cols_reports:
            conn.execute("ALTER TABLE reports ADD COLUMN escalated INTEGER DEFAULT 0;")
        if "escalation_notes" not in cols_reports:
            conn.execute("ALTER TABLE reports ADD COLUMN escalation_notes TEXT;")

    # 6. Add any missing columns to cleanup_tasks safely
    if conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='cleanup_tasks'").fetchone():
        cols_tasks = [r[1] for r in conn.execute("PRAGMA table_info(cleanup_tasks)").fetchall()]
        if "worker_id" not in cols_tasks:
            conn.execute("ALTER TABLE cleanup_tasks ADD COLUMN worker_id INTEGER;")
        if "blocked_reason" not in cols_tasks:
            conn.execute("ALTER TABLE cleanup_tasks ADD COLUMN blocked_reason TEXT;")
        if "worker_notes" not in cols_tasks:
            conn.execute("ALTER TABLE cleanup_tasks ADD COLUMN worker_notes TEXT;")

    # 7. Ensure performance indexes
    conn.execute("CREATE INDEX IF NOT EXISTS idx_reports_status ON reports(status);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_reports_ward ON reports(ward_name);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_reports_uid ON reports(report_uid);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON cleanup_tasks(status);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_worker ON cleanup_tasks(worker_id);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_status_history_report ON report_status_history(report_id);")

    conn.execute("PRAGMA foreign_keys = ON;")


def get_connection(db_path=DB_PATH) -> sqlite3.Connection:
    """Returns a SQLite connection with dict-like row access, migrations, and WAL mode."""
    conn = sqlite3.connect(db_path, timeout=15.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    return conn


def init_db(db_path=DB_PATH):
    """Initializes the database schema if tables do not exist and applies migrations."""
    conn = get_connection(db_path)
    with conn:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
        apply_migrations(conn)
    conn.close()


def reset_db(db_path=DB_PATH):
    """Safely drops and recreates tables for development/testing."""
    conn = get_connection(db_path)
    with conn:
        tables = [
            "report_followups", "report_status_history", "audit_logs",
            "notifications", "cleanup_verifications", "cleanup_tasks",
            "priority_scores", "hotspot_reports", "hotspots", "severity_assessments",
            "detections", "report_images", "reports", "users"
        ]
        for t in tables:
            conn.execute(f"DROP TABLE IF EXISTS {t};")
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
        apply_migrations(conn)
    conn.close()


if __name__ == "__main__":
    init_db()
    print(f"NIRMAAN AI Database successfully initialized and migrated at {DB_PATH}")
