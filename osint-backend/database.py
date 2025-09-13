import sqlite3

DB_FILE = "osint.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    # Table to store OSINT results
    conn.execute("""
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        query TEXT NOT NULL,
        source TEXT NOT NULL,
        data TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()
