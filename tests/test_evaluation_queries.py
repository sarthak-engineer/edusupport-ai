from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_valid_open_ticket_query():
    response = client.post("/query", json={"question": "How many tickets are currently open?"})
    assert response.status_code == 200
    data = response.json()
    assert data["result"]["count"] == 111

def test_average_technical_resolution_query():
    response = client.post("/query", json={"question": "What is the average resolution time for Technical tickets?"})
    assert response.status_code == 200
    data = response.json()
    assert data["result"]["aggregation"] == "avg"
    assert data["result"]["aggregation_field"] == "resolution_time_hrs"

def test_top_agent_query():
    response = client.post("/query", json={"question": "Which agent resolved the most tickets?"})
    assert response.status_code == 200
    data = response.json()
    assert data["plan"]["intent"] == "group_by"
    assert data["plan"]["group_by"] == "agent_id"

def test_high_or_critical_unresolved_query():
    response = client.post("/query", json={"question": "How many unresolved High or Critical tickets are older than 24 hours?"})
    assert response.status_code == 200
    data = response.json()
    assert data["result"]["count"] == 77
    
    # Regression check: Make sure we didn't mistakenly filter for "status = Resolved"
    plan = data["plan"]
    status_filters = [f for f in plan.get("filters", []) if f["field"] == "status"]
    if status_filters:
        # If it used a direct filter, it must be != Resolved (or equivalent)
        for f in status_filters:
            assert not (f["operator"] == "eq" and f["value"] == "Resolved"), "System incorrectly filtered for Resolved instead of Unresolved"
    else:
        # Check filter_groups just in case
        groups = plan.get("filter_groups", [])
        for group in groups:
            for f in group.get("conditions", []):
                if f["field"] == "status":
                    assert not (f["operator"] == "eq" and f["value"] == "Resolved"), "System incorrectly filtered for Resolved instead of Unresolved"

def test_explanation_is_generated():
    response = client.post("/query", json={"question": "How many tickets are currently open?"})
    assert response.status_code == 200
    data = response.json()
    assert "explanation" in data["plan"]
    assert len(data["plan"]["explanation"]) > 0

def test_explanation_reflects_actual_queryplan_fields():
    response = client.post("/query", json={"question": "How many tickets are currently open?"})
    assert response.status_code == 200
    explanation = response.json()["plan"]["explanation"].lower()
    assert "status" in explanation
    assert "open" in explanation

def test_gibberish_query_rejected():
    response = client.post("/query", json={"question": "dsjkbfiwedfiu"})
    assert response.status_code == 200
    data = response.json()
    assert data["plan"]["query_status"] == "unclear"
    assert "error" in data["result"]
    assert "I couldn't interpret" in data["result"]["error"]

def test_unrelated_question_rejected():
    response = client.post("/query", json={"question": "What is the weather in Bengaluru?"})
    assert response.status_code == 200
    data = response.json()
    assert data["plan"]["query_status"] == "out_of_scope"
    assert "error" in data["result"]
    assert "I couldn't interpret" in data["result"]["error"]

def test_semantic_search_like_query():
    response = client.post("/query", json={"question": "payment problems"})
    assert response.status_code == 200
    data = response.json()
    assert data["plan"]["query_status"] == "semantic_search"
    assert "error" in data["result"]
    assert "Use Semantic Search" in data["result"]["error"]

def test_unsupported_analytical_request():
    response = client.post("/query", json={"question": "Predict ticket volume next month."})
    assert response.status_code == 200
    data = response.json()
    assert data["plan"]["query_status"] == "unsupported"
    assert "error" in data["result"]
    assert "not currently supported" in data["result"]["error"]

def test_broad_valid_query_returns_500():
    response = client.post("/query", json={"question": "Show me all tickets"})
    assert response.status_code == 200
    data = response.json()
    assert data["plan"]["query_status"] == "supported"
    assert data["result"]["count"] == 500

def test_anomaly_query_resolution_times():
    response = client.post("/query", json={"question": "Are there any anomalies in resolution times this week?"})
    assert response.status_code == 200
    data = response.json()
    assert data["plan"]["query_status"] == "supported"
    assert data["plan"]["intent"] == "anomaly"
    assert "count" in data["result"]
    assert "rows" in data["result"]

def test_overview_analytics_values():
    response = client.get("/analytics/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total_tickets"] == 500
    assert data["open_tickets"] == 111
    assert data["resolved_tickets"] == 327
    assert data["escalated_tickets"] == 62
    assert data["critical_tickets"] == 55
    assert data["anomaly_count"] == 126
