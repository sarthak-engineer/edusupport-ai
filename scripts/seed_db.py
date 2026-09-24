import pandas as pd
import random
import sys
from pathlib import Path
from datetime import datetime, timedelta

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))
from app.data.db import get_connection, init_db, log_activity

# Realistic subjects by category
SUBJECTS = {
    'Fees': ["Fee receipt not generated", "Discrepancy in tuition fee", "Late fee wrongly charged", "Need fee structure for next semester", "Payment failed but amount deducted"],
    'Hostel': ["Room allocation issue", "Hostel wifi not working", "Request for room change", "Mess food quality complaint", "Maintenance issue in bathroom"],
    'Transport': ["Bus pass not issued", "Bus route query", "Bus timing mismatch", "Request for new stop", "Driver driving rashly"],
    'Technical Support': ["LMS login failing", "Cannot access student portal", "Password reset link not working", "Course registration portal crashing", "Email account locked"],
    'Attendance': ["Attendance marked absent by mistake", "Medical leave application", "Attendance sync issue", "Query about minimum attendance", "Need attendance report"],
    'Examination': ["Hall ticket not downloading", "Exam schedule clash", "Result not showing", "Re-evaluation request", "Grade card discrepancy"],
    'ID Card': ["ID card lost", "Name spelling wrong on ID", "Request for new ID card", "ID card not scanning at gate"],
    'Certificates': ["Bonafide certificate request", "Provisional degree certificate delay", "Migration certificate application", "Transcript request"],
    'Documents': ["Original marksheet return", "Document verification pending", "Submit scholarship documents", "Upload error for document"],
    'General': ["Library timing query", "Request for campus map", "Lost and found inquiry", "Alumni meet details", "Sports complex access"]
}

def seed_database():
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM ticket_activity")
    cursor.execute("DELETE FROM tickets")
    conn.commit()
    
    csv_path = PROJECT_ROOT / "data" / "support_tickets.csv"
    if not csv_path.exists():
        print(f"CSV not found at {csv_path}")
        return
        
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    
    # Calculate date shift
    df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
    max_date = df['created_at'].max()
    now = datetime.now()
    time_shift = now - max_date if pd.notnull(max_date) else timedelta(days=0)
    
    student_names = ["Alice Smith", "Bob Johnson", "Charlie Davis", "Diana Miller", "Eva Wilson", "Frank Moore", "Grace Taylor", "Henry Anderson"]
    demo_student_id = "STU1234"
    demo_student_name = "Demo Student"
    
    for i, row in df.iterrows():
        old_cat = str(row['category']).strip()
        
        if old_cat == 'Billing':
            category = random.choice(['Fees', 'Hostel', 'Transport'])
        elif old_cat == 'Technical':
            category = 'Technical Support'
        else:
            category = random.choice(['General', 'Attendance', 'Examination', 'ID Card', 'Certificates', 'Documents'])
            
        ticket_id = str(row['ticket_id']).strip()
        
        # Ensure STU1234 gets ~10% of tickets
        if random.random() < 0.1:
            student_id = demo_student_id
            student_name = demo_student_name
        else:
            student_id = f"STU{random.randint(1000, 9999)}"
            student_name = random.choice(student_names)
        
        subject = random.choice(SUBJECTS[category])
        description = f"Student {student_name} reported: {subject}. I am facing this issue since yesterday. Please resolve ASAP."
        priority = str(row['priority']).strip()
        status = str(row['status']).strip()
        
        if status == 'Open':
            status = 'NEW' if random.random() > 0.5 else 'IN_PROGRESS'
        elif status == 'Resolved':
            status = 'RESOLVED'
        elif status == 'Escalated':
            status = 'ESCALATED'
            
        assigned_agent = str(row['agent_id']).strip()
        if pd.isna(assigned_agent) or assigned_agent == 'nan' or random.random() < 0.05:
            assigned_agent = None
            if status not in ('NEW', 'CLOSED'):
                status = 'NEW'
                
        created_at = row['created_at']
        if pd.isna(created_at):
            created_at = now - timedelta(days=random.randint(1, 30))
        else:
            created_at = created_at + time_shift
            
        # Ensure updated_at is sensible
        if status in ('RESOLVED', 'CLOSED'):
            # It was resolved in the past
            updated_at = created_at + timedelta(hours=random.uniform(1, 48))
            if updated_at > now:
                updated_at = now - timedelta(hours=1)
        else:
            updated_at = created_at + timedelta(hours=random.uniform(0.5, 4))
            if updated_at > now:
                updated_at = now
        
        resolution_notes = "Resolved as per standard college guidelines. Issue closed." if status == 'RESOLVED' else None
        escalation_reason = "SLA breached or high priority issue needing dean's attention." if status == 'ESCALATED' else None
        
        cursor.execute("""
            INSERT OR REPLACE INTO tickets 
            (ticket_id, student_id, student_name, category, subject, description, priority, status, assigned_agent, created_at, updated_at, resolution_notes, escalation_reason)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ticket_id, student_id, student_name, category, subject, description, priority, status, assigned_agent, 
            created_at.isoformat(), updated_at.isoformat(), resolution_notes, escalation_reason
        ))
        
        # Add a baseline activity log
        log_activity(ticket_id, student_id, "student", "CREATED", "Ticket opened.", conn=conn)
        if assigned_agent:
            log_activity(ticket_id, assigned_agent, "staff", "ASSIGNED", f"Assigned to {assigned_agent}", conn=conn)
        if status == 'RESOLVED':
            log_activity(ticket_id, assigned_agent, "staff", "RESOLVED", "Ticket marked as resolved.", conn=conn)
            
    conn.commit()
    conn.close()
    print("Database seeded successfully with Student Support domain and shifted dates.")

if __name__ == "__main__":
    seed_database()
