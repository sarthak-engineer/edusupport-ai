from fastapi import APIRouter, HTTPException, Query
from app.retrieval.service import SemanticSearchService
from app.retrieval.models import SemanticSearchResult

router = APIRouter(
    prefix="/search/semantic",
    tags=["Semantic Search"],
)

search_service = None

def get_search_service() -> SemanticSearchService:
    global search_service
    if search_service is None:
        search_service = SemanticSearchService()
    return search_service

@router.get("")
def search_tickets(
    q: str = Query(..., description="The natural-language query to search for."),
    top_k: int = Query(5, ge=1, le=20, description="The maximum number of results to return.")
):
    if not q.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
        
    try:
        service = get_search_service()
        results = service.search(q, top_k)
        return {
            "query": q,
            "results": [r.model_dump() for r in results]
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
