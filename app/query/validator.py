from __future__ import annotations

from app.query.schema import QueryPlan


ALLOWED_FIELDS = {
    "ticket_id",
    "created_at",
    "category",
    "priority",
    "status",
    "response_time_hrs",
    "resolution_time_hrs",
    "agent_id",
    "customer_rating",
    "issue_summary",
}

ALLOWED_FILTER_OPERATORS = {
    "eq",
    "neq",
    "gt",
    "gte",
    "lt",
    "lte",
    "contains",
}

ALLOWED_AGGREGATIONS = {
    "count",
    "sum",
    "avg",
    "min",
    "max",
}


def validate_query_plan(plan: QueryPlan) -> QueryPlan:
    """Validate that an LLM-generated query plan is supported."""

    for condition in plan.filters:
        if condition.field not in ALLOWED_FIELDS:
            raise ValueError(
                f"Unsupported filter field: {condition.field}"
            )

        if condition.operator not in ALLOWED_FILTER_OPERATORS:
            raise ValueError(
                f"Unsupported filter operator: {condition.operator}"
            )

    for group in plan.filter_groups:
        if group.logic not in {"AND", "OR"}:
            raise ValueError(
                f"Unsupported logic in filter group: {group.logic}"
            )
        for condition in group.conditions:
            if condition.field not in ALLOWED_FIELDS:
                raise ValueError(
                    f"Unsupported filter field in group: {condition.field}"
                )

            if condition.operator not in ALLOWED_FILTER_OPERATORS:
                raise ValueError(
                    f"Unsupported filter operator in group: {condition.operator}"
                )

    if plan.group_by is not None:
        if plan.group_by not in ALLOWED_FIELDS:
            raise ValueError(
                f"Unsupported group-by field: {plan.group_by}"
            )

    if plan.aggregation is not None:
        if plan.aggregation not in ALLOWED_AGGREGATIONS:
            raise ValueError(
                f"Unsupported aggregation: {plan.aggregation}"
            )

    if plan.aggregation_field is not None:
        if plan.aggregation_field not in ALLOWED_FIELDS:
            raise ValueError(
                f"Unsupported aggregation field: {plan.aggregation_field}"
            )

    if plan.sort_order not in {"asc", "desc"}:
        raise ValueError(
            f"Unsupported sort order: {plan.sort_order}"
        )

    if plan.limit is not None:
        if plan.limit <= 0 or plan.limit > 100:
            raise ValueError(
                "Limit must be between 1 and 100."
            )

    return plan
