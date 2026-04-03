import sqlite3
import os

# Absolute DB path (VERY IMPORTANT)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "system_data.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def create_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        cpu REAL,
        ram REAL,
        disk REAL,
        battery REAL
    )
    """)

    conn.commit()
    conn.close()