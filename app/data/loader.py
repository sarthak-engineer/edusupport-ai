from pathlib import Path
import pandas as pd
import sqlite3

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "data" / "edusupport.db"

def load_support_tickets() -> pd.DataFrame:
    """Load and normalize the support ticket dataset from SQLite."""
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found at: {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM tickets", conn)
    conn.close()

    # Parse date columns
    for column in ["created_at", "updated_at"]:
        if column in df.columns:
            df[column] = pd.to_datetime(df[column], errors="coerce")
            
    # For compatibility with older code expecting resolution_time_hrs
    if 'created_at' in df.columns and 'updated_at' in df.columns:
        df['resolution_time_hrs'] = (df['updated_at'] - df['created_at']).dt.total_seconds() / 3600.0
        
    # Map subject to issue_summary for semantic search backward compatibility
    if 'subject' in df.columns:
        df['issue_summary'] = df['subject']
        
    if 'assigned_agent' in df.columns:
        df['agent_id'] = df['assigned_agent']
        
    # Mock customer rating
    df['customer_rating'] = 4.5

    return df
