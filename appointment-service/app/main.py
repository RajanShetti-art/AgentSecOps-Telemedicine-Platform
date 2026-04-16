"""Appointment service application entrypoint."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import settings
from app.logging_config import configure_logging
from app.models import appointment  # noqa: F401
from app.routes.appointments import router as appointment_router

configure_logging()
app = FastAPI(title=settings.app_name, version=settings.app_version)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(appointment_router)

# Expose Prometheus metrics endpoint at /metrics for observability stack.
Instrumentator().instrument(app).expose(app)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    """Returns service health status."""
    return {"status": "ok", "service": settings.app_name}
