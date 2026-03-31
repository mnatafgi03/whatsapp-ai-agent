import sqlite3

DB_PATH = 'memory.db'


def init_db():
    """Create the messages table if it doesn't exist yet."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            phone     TEXT NOT NULL,
            role      TEXT NOT NULL,
            content   TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


def save_message(phone: str, role: str, content: str):
    """Save one message to the database.

    role must be 'user' or 'model' — Gemini's required format.
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        'INSERT INTO messages (phone, role, content) VALUES (?, ?, ?)',
        (phone, role, content)
    )
    conn.commit()
    conn.close()


def get_history(phone: str, limit: int = 20) -> list:
    """Load the last N messages for a phone number, formatted for Gemini.

    Gemini expects history as a list of dicts like:
    [{'role': 'user', 'parts': [{'text': '...'}]}, ...]
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT role, content FROM messages
        WHERE phone = ?
        ORDER BY timestamp DESC
        LIMIT ?
    ''', (phone, limit))
    rows = c.fetchall()
    conn.close()

    # DB gives us newest-first, we need oldest-first for Gemini
    history = []
    for role, content in reversed(rows):
        history.append({
            'role': role,
            'parts': [{'text': content}]
        })

    return history


# Run once when this file is imported — creates the DB if needed
init_db()
