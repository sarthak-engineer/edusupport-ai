from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_semantic_search_success():
    response = client.get("/search/semantic?q=login&top_k=3")
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "login"
    assert "results" in data
    assert len(data["results"]) <= 3
    
    if data["results"]:
        first = data["results"][0]
        assert "ticket_id" in first
        assert "similarity" in first
        assert "issue_summary" in first
        assert "category" in first
        assert "priority" in first
        assert "status" in first
        assert "agent_id" in first
        assert "created_at" in first
        assert isinstance(first["similarity"], float)

def test_semantic_search_sorting():
    response = client.get("/search/semantic?q=payment&top_k=5")
    assert response.status_code == 200
    results = response.json().get("results", [])
    
    similarities = [r["similarity"] for r in results]
    assert similarities == sorted(similarities, reverse=True)

def test_semantic_search_empty_query():
    response = client.get("/search/semantic?q=&top_k=3")
    assert response.status_code in (400, 422)

def test_semantic_search_whitespace_query():
    response = client.get("/search/semantic?q=   &top_k=3")
    assert response.status_code in (400, 422)

def test_semantic_search_invalid_top_k():
    response = client.get("/search/semantic?q=test&top_k=0")
    assert response.status_code == 422
    
    response = client.get("/search/semantic?q=test&top_k=21")
    assert response.status_code == 422

def test_semantic_search_top_k_limits():
    for k in [3, 5, 10]:
        response = client.get(f"/search/semantic?q=test&top_k={k}")
        assert response.status_code == 200
        assert len(response.json()["results"]) <= k

def test_embedder_is_cached():
    from app.retrieval.embedder import get_embedder
    embedder1 = get_embedder()
    embedder2 = get_embedder()
    assert embedder1 is embedder2
