from __future__ import annotations

from app.llm.base import LLMProvider
from app.query.schema import QueryPlan
from app.query.validator import validate_query_plan


class QueryPlanner:
    """Convert natural-language questions into validated query plans."""

    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider

    def plan(self, question: str) -> QueryPlan:
        question = question.strip()

        if not question:
            raise ValueError(
                "Question cannot be empty."
            )

        plan = self.llm_provider.generate_query_plan(
            question
        )

        return validate_query_plan(plan)
