import sqlite3
import os
from datetime import datetime

_DATA_DIR = os.environ.get("SM_DATA_DIR", os.path.dirname(__file__))
DB_PATH = os.path.join(_DATA_DIR, "salary_manager.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            title TEXT NOT NULL,
            base_salary REAL NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS monthly_income (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            year INTEGER NOT NULL,
            month INTEGER NOT NULL,
            income REAL NOT NULL,
            note TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(user_id, year, month)
        );
    """)
    conn.commit()
    conn.close()


# ── Users ────────────────────────────────────────────────────────────────────

def get_users():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM users ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_user(name: str, title: str, base_salary: float):
    conn = get_conn()
    cur = conn.execute(
        "INSERT INTO users (name, title, base_salary) VALUES (?, ?, ?)",
        (name, title, base_salary),
    )
    conn.commit()
    user_id = cur.lastrowid
    conn.close()
    return user_id


def update_user(user_id: int, name: str, title: str, base_salary: float):
    conn = get_conn()
    conn.execute(
        "UPDATE users SET name=?, title=?, base_salary=? WHERE id=?",
        (name, title, base_salary, user_id),
    )
    conn.commit()
    conn.close()


# ── Monthly Income ────────────────────────────────────────────────────────────

def upsert_income(user_id: int, year: int, month: int, income: float, note: str = ""):
    conn = get_conn()
    conn.execute(
        """INSERT INTO monthly_income (user_id, year, month, income, note)
           VALUES (?, ?, ?, ?, ?)
           ON CONFLICT(user_id, year, month) DO UPDATE SET income=excluded.income, note=excluded.note""",
        (user_id, year, month, income, note),
    )
    conn.commit()
    conn.close()


def get_income_history(user_id: int):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM monthly_income WHERE user_id=? ORDER BY year DESC, month DESC",
        (user_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_income(income_id: int):
    conn = get_conn()
    conn.execute("DELETE FROM monthly_income WHERE id=?", (income_id,))
    conn.commit()
    conn.close()


def get_income_for_stats(user_id: int):
    """Return income sorted oldest-first for analytics."""
    conn = get_conn()
    rows = conn.execute(
        "SELECT year, month, income FROM monthly_income WHERE user_id=? ORDER BY year, month",
        (user_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
