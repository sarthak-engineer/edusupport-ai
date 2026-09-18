from pydantic import BaseModel

class SemanticSearchResult(BaseModel):
    ticket_id: str
    similarity: float
    issue_summary: str
    category: str
    priority: str
    status: str
    agent_id: str
    created_at: str
