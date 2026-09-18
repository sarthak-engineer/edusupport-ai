from fastapi import APIRouter

from app.analytics.service import AnalyticsService

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)

analytics_service = AnalyticsService()


@router.get("/summary")
def get_summary():
    return analytics_service.get_kpi_summary()


@router.get("/agents")
def get_agent_performance():
    result = analytics_service.get_agent_performance()

    return {
        "results": result.to_dict(orient="records")
    }


@router.get("/categories")
def get_category_performance():
    result = analytics_service.get_category_performance()

    return {
        "results": result.to_dict(orient="records")
    }


@router.get("/priorities")
def get_priority_distribution():
    result = analytics_service.get_priority_distribution()

    return {
        "results": result.to_dict(orient="records")
    }
