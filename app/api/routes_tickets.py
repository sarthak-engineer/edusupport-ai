from typing import List, Optional
from fastapi import APIRouter, HTTPException

from app.services.ticket_service import (
    create_ticket, get_ticket, update_ticket, list_tickets,
    TicketCreate, TicketUpdate
)
from app.services.sla_service import calculate_sla

router = APIRouter(prefix="/tickets", tags=["tickets"])

@router.post("", response_model=dict)
def api_create_ticket(data: TicketCreate):
    try:
        return create_ticket(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("", response_model=List[dict])
def api_list_tickets(student_id: Optional[str] = None, agent_id: Optional[str] = None, status: Optional[str] = None):
    try:
        tickets = list_tickets(student_id, agent_id, status)
        for t in tickets:
            t["sla"] = calculate_sla(t)
        return tickets
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{ticket_id}", response_model=dict)
def api_get_ticket(ticket_id: str, user_id: Optional[str] = None, role: Optional[str] = None):
    try:
        ticket = get_ticket(ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
            
        if role and role.lower() == "student":
            if ticket.get("student_id") != user_id:
                raise HTTPException(status_code=403, detail="Access Denied: This ticket belongs to another student.")
                
        ticket["sla"] = calculate_sla(ticket)
        return ticket
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{ticket_id}", response_model=dict)
def api_update_ticket(ticket_id: str, update: TicketUpdate):
    try:
        # Check permissions before updating
        ticket = get_ticket(ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
            
        if update.user_role.lower() == "student":
            if ticket.get("student_id") != update.user_id:
                raise HTTPException(status_code=403, detail="Access Denied: Cannot modify another student's ticket.")
            # Students can only reply
            if update.status or update.priority or update.assigned_agent or update.resolution_notes or update.escalation_reason:
                raise HTTPException(status_code=403, detail="Access Denied: Students cannot modify core ticket fields.")
                
        ticket = update_ticket(ticket_id, update)
        ticket["sla"] = calculate_sla(ticket)
        return ticket
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from app.services.ai_service import AIService
from pydantic import BaseModel

class ClassifyRequest(BaseModel):
    subject: str
    description: str
    
class ResponseRequest(BaseModel):
    ticket_id: str

ai_svc = AIService()

@router.post("/ai/classify")
def api_ai_classify(req: ClassifyRequest):
    return ai_svc.classify_ticket(req.subject, req.description)
    
@router.post("/ai/response")
def api_ai_response(req: ResponseRequest):
    ticket = get_ticket(req.ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    response_text = ai_svc.generate_response(ticket)
    return {"draft_response": response_text}
