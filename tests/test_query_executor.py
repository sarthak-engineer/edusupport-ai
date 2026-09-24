from app.query.executor import QueryExecutor
from app.query.schema import (
    FilterCondition,
    QueryIntent,
    QueryPlan,
)


def test_filter_query():
    executor = QueryExecutor()

    plan = QueryPlan(
        intent=QueryIntent.FILTER,
        filters=[
            FilterCondition(
                field="status",
                operator="eq",
                value="NEW",
            )
        ],
    )

    result = executor.execute(plan)

    assert result["count"] > 0


def test_critical_ticket_count():
    executor = QueryExecutor()

    plan = QueryPlan(
        intent=QueryIntent.AGGREGATE,
        filters=[
            FilterCondition(
                field="priority",
                operator="eq",
                value="Critical",
            )
        ],
        aggregation="count",
    )

    result = executor.execute(plan)

    assert result["value"] > 0


def test_group_by_category():
    executor = QueryExecutor()

    plan = QueryPlan(
        intent=QueryIntent.GROUP_BY,
        group_by="category",
        aggregation="count",
    )

    result = executor.execute(plan)

    assert len(result["results"]) > 3


from app.query.schema import FilterGroup

def test_or_filter_group():
    executor = QueryExecutor()
    plan = QueryPlan(
        intent=QueryIntent.FILTER,
        filter_groups=[
            FilterGroup(
                logic="OR",
                conditions=[
                    FilterCondition(field="priority", operator="eq", value="High"),
                    FilterCondition(field="priority", operator="eq", value="Critical"),
                ]
            )
        ]
    )
    result = executor.execute(plan)
    assert result["count"] > 0

def test_and_plus_or_filter_group():
    executor = QueryExecutor()
    plan = QueryPlan(
        intent=QueryIntent.FILTER,
        filters=[
            FilterCondition(field="status", operator="neq", value="Resolved")
        ],
        filter_groups=[
            FilterGroup(
                logic="OR",
                conditions=[
                    FilterCondition(field="priority", operator="eq", value="High"),
                    FilterCondition(field="priority", operator="eq", value="Critical"),
                ]
            )
        ]
    )
    result = executor.execute(plan)
    assert result["count"] > 0

def test_semantic_date_older_than_24h():
    executor = QueryExecutor()
    plan = QueryPlan(
        intent=QueryIntent.FILTER,
        relative_time="older_than_24_hours"
    )
    result = executor.execute(plan)
    assert result["count"] > 0
