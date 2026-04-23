import sqlite3

def connect():
    conn = sqlite3.connect("portal.db")
    return conn


def init_db():
    conn = connect()
    cur = conn.cursor()

    # Students table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        matric TEXT UNIQUE,
        name TEXT,
        level TEXT
    )
    """)

    # Files table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT,
        filepath TEXT
    )
    """)

    conn.commit()
    conn.close()