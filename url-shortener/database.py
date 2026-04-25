import sqlite3

DB_PATH = "shortener.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Global counter for ID ranges
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS global_counters (
            counter_name TEXT PRIMARY KEY,
            last_id INTEGER NOT NULL
        )
    """)
    
    # URL mapping storage
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS url_mappings (
            id INTEGER PRIMARY KEY,
            short_code TEXT UNIQUE,
            long_url TEXT UNIQUE
        )
    """)
    
    cursor.execute("INSERT OR IGNORE INTO global_counters VALUES ('url_shortener', 0)")
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()