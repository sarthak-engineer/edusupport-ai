from fastapi.testclient import TestClient
from app.main import app
from app.services.ticket_service import create_ticket, TicketCreate

client = TestClient(app)

def test_ticket_creation_and_activity_isolation():
    # 1. Create a ticket
    payload = {
        "student_id": "STU9999",
        "student_name": "Test Student",
        "category": "Fees",
        "subject": "Test Fee Issue",
        "description": "Please help.",
        "priority": "High"
    }
    response = client.post("/tickets", json=payload)
    assert response.status_code == 200
    ticket = response.json()
    
    ticket_id = ticket["ticket_id"]
    
    # 2. Check student ownership
    assert ticket["student_id"] == "STU9999"
    assert ticket["student_id"] != ticket_id
    
    # 3. Check activity isolation
    activities = ticket.get("activity", [])
    assert len(activities) == 1
    assert activities[0]["action_type"] == "CREATED"
    assert activities[0]["user_id"] == "STU9999"
    
    # 4. Assignment
    assign_payload = {
        "assigned_agent": "AGT-99",
        "user_id": "AGT-99",
        "user_role": "staff"
    }
    resp = client.patch(f"/tickets/{ticket_id}", json=assign_payload)
    assert resp.status_code == 200
    updated = resp.json()
    assert updated["assigned_agent"] == "AGT-99"
    
    # Verify assignment activity
    acts = updated["activity"]
    assert len(acts) == 2
    assert acts[0]["action_type"] == "ASSIGNED"
    
    # 5. Add reply
    reply_payload = {
        "reply": "Working on this.",
        "user_id": "AGT-99",
        "user_role": "staff"
    }
    resp = client.patch(f"/tickets/{ticket_id}", json=reply_payload)
    updated2 = resp.json()
    assert len(updated2["activity"]) == 3
    assert updated2["activity"][0]["action_type"] == "REPLY"
    
    # All activities must belong to this ticket
    for act in updated2["activity"]:
        assert act["ticket_id"] == ticket_id

def test_sla_active_vs_resolved():
    payload = {
        "student_id": "STU8888",
        "student_name": "Test Student 2",
        "category": "General",
        "subject": "Test SLA Issue",
        "description": "Help.",
        "priority": "Critical"
    }
    resp = client.post("/tickets", json=payload)
    ticket = resp.json()
    
    # Active SLA
    resp_get = client.get(f"/tickets/{ticket['ticket_id']}")
    assert resp_get.status_code == 200, resp_get.text
    ticket_with_sla = resp_get.json()
    sla = ticket_with_sla.get("sla", {})
    assert sla.get("state") in ("NORMAL", "AT_RISK", "BREACHED")
    
    # Resolve
    resolve_payload = {
        "status": "RESOLVED",
        "resolution_notes": "Fixed.",
        "user_id": "AGT-99",
        "user_role": "staff"
    }
    resp2 = client.patch(f"/tickets/{ticket['ticket_id']}", json=resolve_payload)
    assert resp2.status_code == 200, resp2.text
    resolved = resp2.json()
    
    # Resolved SLA
    sla_resolved = resolved.get("sla", {})
    assert sla_resolved["state"] in ("SLA_MET", "SLA_BREACHED")
