import sys
sys.path.insert(0, ".")
import sqlite3
from pathlib import Path
from src.database.connection import apply_migrations

db_file = Path("data/nirmaan.db")
print("DB file exists:", db_file.exists())
if db_file.exists():
    conn = sqlite3.connect(str(db_file))
    cur = conn.cursor()
    cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='cleanup_tasks'")
    tasks_sql = cur.fetchone()
    print("Tasks SQL:", tasks_sql[0] if tasks_sql else "None")
    cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='reports'")
    reps_sql = cur.fetchone()
    print("Reports SQL:", reps_sql[0] if reps_sql else "None")
    conn.close()
