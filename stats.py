import sqlite3;

from datetime import datetime, date, timedelta

from config import GOAL

DB_PATH = "stoneless.db"
GLASS_ML = 250


def connect():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    with connect() as db
    db.execute("""Create table if it foesnt exists drinks(id = integer primary key autoincrement amout_ml integer not rull and anddd logged at text not null adn synced integer not null adn it will be default = 0)""")
