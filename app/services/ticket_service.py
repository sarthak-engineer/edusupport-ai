from typing import List, Optional
import uuid
from datetime import datetime
from pydantic import BaseModel, Field

from app.data.db import get_connection, log_activity

class TicketCreate(BaseModel):
    student_id: str
    student_name: str
    category: str
    subject: str
    description: str
    priority: str = "Medium"

class TicketUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_agent: Optional[str] = None
    resolution_notes: Optional[str] = None
    escalation_reason: Optional[str] = None
    pending_reason: Optional[str] = None
    reply: Optional[str] = None
    user_id: str
    user_role: str

def create_ticket(data: TicketCreate) -> dict:
    conn = get_connection()
    cursor = conn.cursor()
    
    ticket_id = f"TCK-{uuid.uuid4().hex[:8].upper()}"
    now_iso = datetime.now().isoformat()
    
    cursor.execute("""
        INSERT INTO tickets 
        (ticket_id, student_id, student_name, category, subject, description, priority, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'NEW', ?, ?)
    """, (
        ticket_id, data.student_id, data.student_name, data.category, data.subject, data.description, data.priority, now_iso, now_iso
    ))
    
    log_activity(ticket_id, data.student_id, "student", "CREATED", "Ticket opened by student.", conn=conn)
    
    conn.commit()
    conn.close()
    
    return get_ticket(ticket_id)

def get_ticket(ticket_id: str) -> Optional[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tickets WHERE ticket_id = ?", (ticket_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return None
        
    ticket = dict(row)
    
    cursor.execute("SELECT * FROM ticket_activity WHERE ticket_id = ? ORDER BY created_at DESC", (ticket_id,))
    ticket['activity'] = [dict(act) for act in cursor.fetchall()]
    
    conn.close()
    return ticket

def update_ticket(ticket_id: str, update: TicketUpdate) -> Optional[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM tickets WHERE ticket_id = ?", (ticket_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None
        
    current = dict(row)
    now_iso = datetime.now().isoformat()
    
    updates = []
    params = []
    
    if update.status and update.status != current['status']:
        updates.append("status = ?")
        params.append(update.status)
        log_activity(ticket_id, update.user_id, update.user_role, "STATUS_CHANGE", f"Status changed from {current['status']} to {update.status}", conn=conn)
        
    if update.priority and update.priority != current['priority']:
        updates.append("priority = ?")
        params.append(update.priority)
        log_activity(ticket_id, update.user_id, update.user_role, "PRIORITY_CHANGE", f"Priority changed from {current['priority']} to {update.priority}", conn=conn)
        
    if update.assigned_agent and update.assigned_agent != current['assigned_agent']:
        updates.append("assigned_agent = ?")
        params.append(update.assigned_agent)
        log_activity(ticket_id, update.user_id, update.user_role, "ASSIGNED", f"Assigned to {update.assigned_agent}", conn=conn)
        
    if update.resolution_notes:
        updates.append("resolution_notes = ?")
        params.append(update.resolution_notes)
        log_activity(ticket_id, update.user_id, update.user_role, "RESOLVED", "Ticket resolved.", conn=conn)
        
    if update.escalation_reason:
        updates.append("escalation_reason = ?")
        params.append(update.escalation_reason)
        log_activity(ticket_id, update.user_id, update.user_role, "ESCALATED", f"Escalated: {update.escalation_reason}", conn=conn)
        
    if update.pending_reason and update.status == "PENDING":
        log_activity(ticket_id, update.user_id, update.user_role, "PENDING", f"Pending reason: {update.pending_reason}", conn=conn)
        
    if update.reply:
        log_activity(ticket_id, update.user_id, update.user_role, "REPLY", update.reply, conn=conn)
        
    if updates:
        updates.append("updated_at = ?")
        params.append(now_iso)
        params.append(ticket_id)
        
        query = f"UPDATE tickets SET {', '.join(updates)} WHERE ticket_id = ?"
        cursor.execute(query, params)
        
    conn.commit()
    conn.close()
    
    return get_ticket(ticket_id)

def list_tickets(student_id: Optional[str] = None, agent_id: Optional[str] = None, status: Optional[str] = None) -> List[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM tickets WHERE 1=1"
    params = []
    
    if student_id:
        query += " AND student_id = ?"
        params.append(student_id)
    if agent_id:
        query += " AND assigned_agent = ?"
        params.append(agent_id)
    if status:
        query += " AND status = ?"
        params.append(status)
        
    query += " ORDER BY created_at DESC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]
