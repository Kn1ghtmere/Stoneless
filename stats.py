import os
import sqlite3
from datetime import date, datetime, timedelta

from config import GLASS_ML, GOAL
from paths import data_dir

DB_PATH = os.path.join(data_dir(), "stoneless.db")


def connect():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db


def init_db():
    with connect() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS drinks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount_ml INTEGER NOT NULL,
                logged_at TEXT NOT NULL,
                synced INTEGER NOT NULL DEFAULT 0
            )
        """)


def log_drink(amount_ml=GLASS_ML):
    with connect() as db:
        db.execute(
            "INSERT INTO drinks (amount_ml, logged_at) VALUES (?, ?)",
            (amount_ml, datetime.now().isoformat()),
        )


def today_count():
    today = date.today().isoformat()
    with connect() as db:
        row = db.execute(
            "SELECT COUNT(*) FROM drinks WHERE logged_at LIKE ?", (today + "%",)
        ).fetchone()
    return row[0]


def daily_counts(days=7):
    """[(date_str, glasses), ...] oldest -> newest, zero-filled. Good for charts."""
    start = date.today() - timedelta(days=days - 1)
    with connect() as db:
        rows = db.execute(
            "SELECT substr(logged_at, 1, 10) AS d, COUNT(*) AS n "
            "FROM drinks WHERE d >= ? GROUP BY d",
            (start.isoformat(),),
        ).fetchall()
    counts = {r["d"]: r["n"] for r in rows}
    out = []
    for i in range(days):
        d = (start + timedelta(days=i)).isoformat()
        out.append((d, counts.get(d, 0)))
    return out


def current_streak():
    """Consecutive days with >= GOAL glasses. Today doest break it until the day endzzzzz."""
    with connect() as db:
        rows = db.execute(
            "SELECT substr(logged_at, 1, 10) AS d, COUNT(*) AS n FROM drinks GROUP BY d"
        ).fetchall()
    counts = {r["d"]: r["n"] for r in rows}

    day = date.today()
    if counts.get(day.isoformat(), 0) < GOAL:
        day -= timedelta(days=1)

    streak = 0
    while counts.get(day.isoformat(), 0) >= GOAL:
        streak += 1
        day -= timedelta(days=1)
    return streak


def unsynced():
    with connect() as db:
        return [dict(r) for r in db.execute("SELECT * FROM drinks WHERE synced = 0")]


def mark_synced(ids):
    if not ids:
        return
    marks = ",".join("?" * len(ids))
    with connect() as db:
        db.execute(f"UPDATE drinks SET synced = 1 WHERE id IN ({marks})", ids)