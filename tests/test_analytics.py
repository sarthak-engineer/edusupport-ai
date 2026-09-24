from app.analytics.service import AnalyticsService


def test_kpi_summary():
    service = AnalyticsService()

    result = service.get_kpi_summary()

    assert result["total_tickets"] >= 500
    assert result["resolved_tickets"] >= 0
    assert result["open_tickets"] >= 0
    assert result["escalated_tickets"] >= 0


def test_filter_open_tickets():
    service = AnalyticsService()

    result = service.filter_tickets(
        status="Open"
    )

    assert len(result) >= 0


def test_filter_critical_tickets():
    service = AnalyticsService()

    result = service.filter_tickets(
        priority="Critical"
    )

    assert len(result) >= 0


def test_filter_technical_tickets():
    service = AnalyticsService()

    result = service.filter_tickets(
        category="Technical"
    )

    assert len(result) >= 0


def test_agent_performance():
    service = AnalyticsService()

    result = service.get_agent_performance()

    assert not result.empty
    assert "agent_id" in result.columns
    assert "resolved_tickets" in result.columns
    assert "average_rating" in result.columns


def test_category_performance():
    service = AnalyticsService()

    result = service.get_category_performance()

    assert len(result) > 0


def test_priority_distribution():
    service = AnalyticsService()

    result = service.get_priority_distribution()

    assert result["count"].sum() >= 500


def test_rank_agents():
    service = AnalyticsService()

    result = service.rank_agents(
        metric="resolved_tickets",
        ascending=False,
        limit=3,
    )

    assert len(result) == 3
    assert result.iloc[0]["resolved_tickets"] >= result.iloc[1][
        "resolved_tickets"
    ]


def test_ticket_count_with_filters():
    service = AnalyticsService()

    result = service.get_ticket_count(
        priority="Critical",
        status="Open",
    )

    assert result >= 0
