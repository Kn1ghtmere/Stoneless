import sqlite3

DB_PATH = "server.db"
SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS profiles (
    user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    username TEXT NOT NULL UNIQUE,
    avatar_color TEXT NOT NULL DEFAULT '#4fc3f7',
    daily_goal_ml INTEGER NOT NULL DEFAULT 2000
);

CREATE TABLE IF NOT EXISTS drinks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    client_id INTEGER NOT NULL,
    amount_ml INTEGER NOT NULL,
    logged_at TEXT NOT NULL,
    UNIQUE(user_id, client_id)
);
CREATE INDEX IF NOT EXISTS idx_drinks_user_time ON drinks(user_id, logged_at);

"""



def init_db():
    db = sqlite3.connect(DB_PATH)
    db.executescript(SCHEMA)
    db.close()

def get_db():
    db = sqlite3.connect(DB_PATH, check_same_thread=False)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    try:
        yield db
    finally:
        db.close()