import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "Meshwork.db")

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                date      TEXT NOT NULL,
                gb_shared REAL DEFAULT 0.0,
                uptime_pct REAL DEFAULT 100.0,
                is_gateway INTEGER DEFAULT 0
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                event     TEXT NOT NULL,
                node_id   TEXT
            )
        """)
        conn.commit()

def log_metric(gb_shared: float, uptime_pct: float, is_gateway: bool = False):
    today = datetime.utcnow().strftime("%Y-%m-%d")
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO metrics (date, gb_shared, uptime_pct, is_gateway) VALUES (?, ?, ?, ?)",
            (today, gb_shared, uptime_pct, 1 if is_gateway else 0)
        )
        conn.commit()

def get_metrics_history(days: int = 30) -> list:
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT date, gb_shared, uptime_pct, is_gateway FROM metrics ORDER BY date DESC LIMIT ?",
            (days,)
        ).fetchall()
    return [{"date": r[0], "gb_shared": r[1], "uptime_pct": r[2], "is_gateway": bool(r[3])} for r in reversed(rows)]
