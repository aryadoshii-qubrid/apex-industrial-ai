import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Any

DB_NAME = "apex_industrial.db"

def init_db():
    """Initialize the database tables."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Table 1: Sessions
    # We add 'mode' to store the protocol (Defect/Safety/General)
    c.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            title TEXT,
            image_path TEXT,
            mode TEXT DEFAULT 'General Analysis', 
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Table 2: Messages
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            role TEXT,
            content TEXT,
            usage_data TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(session_id) REFERENCES sessions(id)
        )
    ''')
    conn.commit()
    conn.close()

def create_session(session_id: str, title: str = "New Inspection", mode: str = "General Analysis"):
    """Creates a new session entry with a specific mode."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO sessions (id, title, mode) VALUES (?, ?, ?)", (session_id, title, mode))
    conn.commit()
    conn.close()

def update_session_mode(session_id: str, mode: str):
    """Updates the analysis protocol for a specific session."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Migration hack: If column missing, try to add it (for dev environment safety)
    try:
        c.execute("UPDATE sessions SET mode = ? WHERE id = ?", (mode, session_id))
    except sqlite3.OperationalError:
        try:
            c.execute("ALTER TABLE sessions ADD COLUMN mode TEXT DEFAULT 'General Analysis'")
            c.execute("UPDATE sessions SET mode = ? WHERE id = ?", (mode, session_id))
        except:
            pass
    conn.commit()
    conn.close()

def update_session_image(session_id: str, image_path: str):
    """Links an image file to a specific session."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("UPDATE sessions SET image_path = ? WHERE id = ?", (image_path, session_id))
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()

def get_session_meta(session_id: str) -> Dict:
    """Gets metadata (title, image_path, mode) for a session."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def add_message(session_id: str, role: str, content: str, usage: Dict = None):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    usage_json = json.dumps(usage) if usage else None
    
    c.execute(
        "INSERT INTO messages (session_id, role, content, usage_data) VALUES (?, ?, ?, ?)",
        (session_id, role, content, usage_json)
    )
    
    if role == "user":
        new_title = (content[:30] + '...') if len(content) > 30 else content
        c.execute("UPDATE sessions SET title = ? WHERE id = ? AND title = 'New Inspection'", (new_title, session_id))
        
    conn.commit()
    conn.close()

def get_all_sessions() -> List[Dict]:
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("""
        SELECT DISTINCT s.*
        FROM sessions s
        LEFT JOIN messages m ON s.id = m.session_id
        WHERE m.id IS NOT NULL 
           OR s.image_path IS NOT NULL 
           OR s.title != 'New Inspection'
        ORDER BY s.created_at DESC
    """)
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_session_history(session_id: str) -> List[Dict]:
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM messages WHERE session_id = ? ORDER BY id ASC", (session_id,))
    rows = c.fetchall()
    conn.close()
    
    history = []
    for row in rows:
        msg = {"role": row["role"], "content": row["content"]}
        if row["usage_data"]:
            msg["usage"] = json.loads(row["usage_data"])
        history.append(msg)
    return history

def update_session_title(session_id: str, new_title: str):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE sessions SET title = ? WHERE id = ?", (new_title, session_id))
    conn.commit()
    conn.close()

def delete_session(session_id: str):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT image_path FROM sessions WHERE id = ?", (session_id,))
    row = c.fetchone()
    
    if row and row[0]:
        image_path = row[0]
        if os.path.exists(image_path):
            try:
                os.remove(image_path)
            except Exception as e:
                print(f"Error deleting file: {e}")

    c.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
    c.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
    conn.commit()
    conn.close()