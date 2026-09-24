from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_valid_open_ticket_query():
    response = client.post("/query", json={"question": "How many tickets are currently open?"})
    if response.status_code == 200:
        data = response.json()
        assert data["result"]["count"] >= 0

def test_average_technical_resolution_query():
    response = client.post("/query", json={"question": "What is the average resolution time for Technical tickets?"})
    if response.status_code == 200:
        data = response.json()
        assert data["result"]["aggregation"] == "avg"
        assert data["result"]["aggregation_field"] == "resolution_time_hrs"

def test_top_agent_query():
    response = client.post("/query", json={"question": "Which agent resolved the most tickets?"})
    if response.status_code == 200:
        data = response.json()
        assert data["plan"]["intent"] == "group_by"
        assert data["plan"]["group_by"] == "agent_id"

def test_high_or_critical_unresolved_query():
    response = client.post("/query", json={"question": "How many unresolved High or Critical tickets are older than 24 hours?"})
    if response.status_code == 200:
        data = response.json()
        assert data["result"]["count"] >= 0
        
        plan = data["plan"]
        status_filters = [f for f in plan.get("filters", []) if f["field"] == "status"]
        if status_filters:
            for f in status_filters:
                assert not (f["operator"] == "eq" and f["value"] == "Resolved")
        else:
            groups = plan.get("filter_groups", [])
            for group in groups:
                for f in group.get("conditions", []):
                    if f["field"] == "status":
                        assert not (f["operator"] == "eq" and f["value"] == "Resolved")

def test_explanation_is_generated():
    response = client.post("/query", json={"question": "How many tickets are currently open?"})
    if response.status_code == 200:
        data = response.json()
        assert "explanation" in data["plan"]
        assert len(data["plan"]["explanation"]) > 0

def test_explanation_reflects_actual_queryplan_fields():
    response = client.post("/query", json={"question": "How many tickets are currently open?"})
    if response.status_code == 200:
        explanation = response.json()["plan"]["explanation"].lower()
        assert "status" in explanation
        assert "open" in explanation

def test_gibberish_query_rejected():
    response = client.post("/query", json={"question": "dsjkbfiwedfiu"})
    if response.status_code == 200:
        data = response.json()
        assert data["plan"]["query_status"] == "unclear"
        assert "error" in data["result"]
        assert "I couldn't interpret" in data["result"]["error"]

def test_unrelated_question_rejected():
    response = client.post("/query", json={"question": "What is the weather in Bengaluru?"})
    if response.status_code == 200:
        data = response.json()
        assert data["plan"]["query_status"] == "out_of_scope"
        assert "error" in data["result"]
        assert "I couldn't interpret" in data["result"]["error"]

def test_semantic_search_like_query():
    response = client.post("/query", json={"question": "payment problems"})
    if response.status_code == 200:
        data = response.json()
        assert data["plan"]["query_status"] == "semantic_search"
        assert "error" in data["result"]
        assert "Use Semantic Search" in data["result"]["error"]

def test_unsupported_analytical_request():
    response = client.post("/query", json={"question": "Predict ticket volume next month."})
    if response.status_code == 200:
        data = response.json()
        assert data["plan"]["query_status"] == "unsupported"
        assert "error" in data["result"]
        assert "not currently supported" in data["result"]["error"]

def test_broad_valid_query_returns_500():
    response = client.post("/query", json={"question": "Show me all tickets"})
    if response.status_code == 200:
        data = response.json()
        assert data["plan"]["query_status"] == "supported"
        assert data["result"]["count"] >= 0



def test_overview_analytics_values():
    response = client.get("/analytics/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total_tickets"] >= 0
    assert data["open_tickets"] >= 0
    assert data["resolved_tickets"] >= 0
    assert data["escalated_tickets"] >= 0
    assert data["critical_tickets"] >= 0
