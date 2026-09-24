import sqlite3
import json
import os
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "data" / "edusupport.db"

def get_connection():
    os.makedirs(DB_PATH.parent, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create tickets table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tickets (
        ticket_id TEXT PRIMARY KEY,
        student_id TEXT,
        student_name TEXT,
        category TEXT,
        subject TEXT,
        description TEXT,
        priority TEXT,
        status TEXT,
        assigned_agent TEXT,
        created_at DATETIME,
        updated_at DATETIME,
        resolution_notes TEXT,
        escalation_reason TEXT
    )
    """)
    
    # Create activity table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ticket_activity (
        activity_id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticket_id TEXT,
        user_id TEXT,
        user_role TEXT,
        action_type TEXT,
        details TEXT,
        created_at DATETIME,
        FOREIGN KEY (ticket_id) REFERENCES tickets(ticket_id)
    )
    """)
    
    conn.commit()
    conn.close()

def log_activity(ticket_id: str, user_id: str, user_role: str, action_type: str, details: str, conn=None):
    close_conn = False
    if conn is None:
        conn = get_connection()
        close_conn = True
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO ticket_activity (ticket_id, user_id, user_role, action_type, details, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (ticket_id, user_id, user_role, action_type, details, datetime.now().isoformat()))
    if close_conn:
        conn.commit()
        conn.close()
    
if __name__ == "__main__":
    init_db()
    print("Database initialized.")
