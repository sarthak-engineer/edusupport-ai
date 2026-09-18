from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.llm.groq_provider import GroqProvider
from app.query.executor import QueryExecutor
from app.query.planner import QueryPlanner
from app.query.explainer import explain_plan

router = APIRouter(
    prefix="/query",
    tags=["Natural Language Query"],
)


class QueryRequest(BaseModel):
    question: str


@router.post("")
def query_support_tickets(request: QueryRequest):
    try:
        planner = QueryPlanner(
            GroqProvider()
        )

        plan = planner.plan(
            request.question
        )
        
        if plan.query_status != "supported":
            plan_dict = plan.model_dump()
            return {
                "question": request.question,
                "plan": plan_dict,
                "result": {"error": plan.message or "Unsupported query"}
            }

        executor = QueryExecutor()

        result = executor.execute(plan)
        
        plan_dict = plan.model_dump()
        plan_dict["explanation"] = explain_plan(plan, result)

        return {
            "question": request.question,
            "plan": plan_dict,
            "result": result,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
