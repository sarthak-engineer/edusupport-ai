from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class QueryIntent(str, Enum):
    FILTER = "filter"
    AGGREGATE = "aggregate"
    GROUP_BY = "group_by"
    TREND = "trend"
    COMPARISON = "comparison"



class QueryStatus(str, Enum):
    SUPPORTED = "supported"
    UNSUPPORTED = "unsupported"
    OUT_OF_SCOPE = "out_of_scope"
    UNCLEAR = "unclear"
    SEMANTIC_SEARCH = "semantic_search"


class FilterCondition(BaseModel):
    field: str
    operator: str
    value: Any


class FilterGroup(BaseModel):
    logic: str
    conditions: list[FilterCondition]


class QueryPlan(BaseModel):
    query_status: QueryStatus = QueryStatus.SUPPORTED
    message: str | None = None
    
    intent: QueryIntent | None = None

    filters: list[FilterCondition] = Field(default_factory=list)
    filter_groups: list[FilterGroup] = Field(default_factory=list)

    group_by: str | None = None

    aggregation: str | None = None
    aggregation_field: str | None = None

    sort_by: str | None = None
    sort_order: str = "desc"

    limit: int | None = None

    start_date: str | None = None
    end_date: str | None = None
    relative_time: str | None = None
