from contextlib import asynccontextmanager

from fastapi import FastAPI, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, generate_latest

from src.infra.database import init_db
from src.infra.messaging import start_consumer_task
from src.modules.doctorDashboard.api.router import router as doctor_dashboard_router
from src.modules.operationsCenter.api.router import router as operations_center_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    start_consumer_task()
    yield


app = FastAPI(
    title="Analytic Service",
    version="1.0.0",
    description="Dashboards analiticos por contexto de feature.",
    lifespan=lifespan,
)

dashboard_requests = Counter(
    "analytic_dashboard_requests_total",
    "Total dashboard requests by analytic context.",
    ["context"],
)
active_business_alerts = Gauge(
    "analytic_active_business_alerts",
    "Active business alerts reported by the analytic service.",
)

app.include_router(doctor_dashboard_router, prefix="/analytics")
app.include_router(operations_center_router, prefix="/analytics")


@app.middleware("http")
async def count_dashboard_requests(request, call_next):
    if request.url.path.startswith("/analytics/doctors"):
        dashboard_requests.labels(context="doctor").inc()
    if request.url.path.startswith("/analytics/operations"):
        dashboard_requests.labels(context="operations_center").inc()
    return await call_next(request)


@app.get("/analytics/health", tags=["health"])
def health_check():
    return {"status": "ok"}


@app.get("/analytics/metrics", tags=["observability"])
def metrics():
    active_business_alerts.set(2)
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


def main():
    import uvicorn

    uvicorn.run("src.server:app", host="127.0.0.1", port=8005, reload=True)
