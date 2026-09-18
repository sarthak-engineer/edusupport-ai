from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_anomalies import router as anomalies_router
from app.api.routes_analytics import router as analytics_router
from app.api.routes_health import router as health_router
from app.api.routes_query import router as query_router
from app.api.routes_search import router as search_router

from fastapi.responses import RedirectResponse

app = FastAPI(
    title="AI Support Intelligence Platform",
    description=(
        "AI-powered support ticket analytics with "
        "natural-language querying and explainable anomaly detection."
    ),
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", include_in_schema=False)
def read_root():
    return RedirectResponse(url="/docs")


app.include_router(health_router)
app.include_router(query_router)
app.include_router(analytics_router)
app.include_router(anomalies_router)
app.include_router(search_router)
