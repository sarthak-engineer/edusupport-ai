from __future__ import annotations

from typing import Protocol

from app.query.schema import QueryPlan


class LLMProvider(Protocol):
    """Interface for LLM query-planning providers."""

    def generate_query_plan(self, question: str) -> QueryPlan:
        ...
