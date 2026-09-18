from __future__ import annotations

import json
import os

from dotenv import load_dotenv
from groq import Groq

from app.llm.prompts import SYSTEM_PROMPT
from app.query.schema import QueryPlan


load_dotenv(override=True)


class GroqProvider:
    """Generate structured query plans using Groq."""

    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError(
                "GROQ_API_KEY is not configured."
            )

        self.client = Groq(api_key=api_key)

        self.model = os.getenv(
            "GROQ_MODEL",
            "openai/gpt-oss-120b",
        )

    def generate_query_plan(
        self,
        question: str,
    ) -> QueryPlan:

        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": question,
                },
            ],
        )

        content = response.choices[0].message.content

        if not content:
            raise ValueError(
                "LLM returned an empty response."
            )

        try:
            data = json.loads(content)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "LLM returned invalid JSON."
            ) from exc

        if "error" in data:
            raise ValueError(data["error"])

        from pydantic import ValidationError
        try:
            return QueryPlan.model_validate(data)
        except ValidationError:
            raise ValueError(
                "I couldn't map that question to a supported support-ticket analysis. Please ask about ticket status, priority, category, agents, resolution time, ratings, or dates."
            )
