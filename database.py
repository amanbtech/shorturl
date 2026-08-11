import sqlite3
from config import DATABASE_URL


conn = sqlite3.connect(
    DATABASE_URL,
    check_same_thread=False
)


def get_cursor():
    return conn.cursor()


def init_database():
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS url_shortener(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_url TEXT,
            short_code TEXT UNIQUE,
            clicks INTEGER DEFAULT 0,
            creating_time TEXT NOT NULL,
            username TEXT NOT NULL,
            expires_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            password_hash TEXT UNIQUE,
            role TEXT DEFAULT 'user'
        )
    """)

    conn.commit()