from datetime import datetime
from typing import Dict, Any

SLA_LIMITS = {
    "Critical": 4.0,
    "High": 8.0,
    "Medium": 24.0,
    "Low": 48.0
}

def calculate_sla(ticket: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate SLA metrics for a given ticket."""
    priority = ticket.get("priority", "Medium")
    limit_hours = SLA_LIMITS.get(priority, 24.0)
    
    created_at_str = ticket.get("created_at")
    if not created_at_str:
        return _default_sla(limit_hours)
        
    try:
        created_at = datetime.fromisoformat(created_at_str)
    except ValueError:
        return _default_sla(limit_hours)
        
    status = ticket.get("status", "NEW")
    if status in ("RESOLVED", "CLOSED"):
        # For resolved tickets, elapsed time stops at updated_at
        updated_at_str = ticket.get("updated_at")
        try:
            end_time = datetime.fromisoformat(updated_at_str) if updated_at_str else datetime.now()
        except ValueError:
            end_time = datetime.now()
    else:
        end_time = datetime.now()
        
    elapsed_time = end_time - created_at
    elapsed_hours = elapsed_time.total_seconds() / 3600.0
    
    remaining_hours = max(0, limit_hours - elapsed_hours)
    percentage_consumed = (elapsed_hours / limit_hours) * 100
    
    if status in ("RESOLVED", "CLOSED"):
        if percentage_consumed < 100:
            state = "SLA_MET"
        else:
            state = "SLA_BREACHED"
    else:
        if percentage_consumed < 80:
            state = "NORMAL"
        elif percentage_consumed < 100:
            state = "AT_RISK"
        else:
            state = "BREACHED"
        
    return {
        "limit_hours": limit_hours,
        "elapsed_hours": round(elapsed_hours, 2),
        "remaining_hours": round(remaining_hours, 2),
        "percentage_consumed": round(percentage_consumed, 1),
        "state": state
    }

def _default_sla(limit_hours: float) -> Dict[str, Any]:
    return {
        "limit_hours": limit_hours,
        "elapsed_hours": 0.0,
        "remaining_hours": limit_hours,
        "percentage_consumed": 0.0,
        "state": "NORMAL"
    }
