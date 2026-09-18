import numpy as np
from app.data.repository import get_support_tickets
from app.retrieval.embedder import get_embedder
from app.retrieval.models import SemanticSearchResult

class SemanticSearchService:
    def __init__(self):
        self.df = get_support_tickets()
        self.embedder = get_embedder()
        
        # Precompute embeddings on startup
        if "issue_summary" in self.df.columns:
            summaries = self.df["issue_summary"].fillna("").tolist()
            self.document_embeddings = self.embedder.encode(summaries)
        else:
            self.document_embeddings = np.array([])

    def search(self, query: str, top_k: int = 5) -> list[SemanticSearchResult]:
        if not query.strip():
            return []
            
        if self.document_embeddings.size == 0 or self.df.empty:
            return []
            
        # Embed the query
        query_embedding = self.embedder.encode([query])[0]
        
        # Compute cosine similarity
        # Since embeddings are normalized (L2 norm = 1), dot product = cosine similarity
        similarities = np.dot(self.document_embeddings, query_embedding)
        
        # Get top-k indices descending
        top_k_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_k_indices:
            row = self.df.iloc[idx]
            sim = round(float(similarities[idx]), 4)
            
            result = SemanticSearchResult(
                ticket_id=str(row.get("ticket_id", "")),
                similarity=sim,
                issue_summary=str(row.get("issue_summary", "")),
                category=str(row.get("category", "")),
                priority=str(row.get("priority", "")),
                status=str(row.get("status", "")),
                agent_id=str(row.get("agent_id", "")),
                created_at=str(row.get("created_at", ""))
            )
            results.append(result)
            
        return results
