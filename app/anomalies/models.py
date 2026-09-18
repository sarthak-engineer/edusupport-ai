from __future__ import annotations

from pydantic import BaseModel


class Anomaly(BaseModel):
    ticket_id: str
    anomaly_type: str
    severity: str
    reason: str
    value: float | None = None
