"""Appointment service application entrypoint."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.logging_config import configure_logging
from app.metrics import setup_metrics
from app.models import appointment  # noqa: F401
from app.routes.appointments import router as appointment_router

configure_logging()
app = FastAPI(title=settings.app_name, version=settings.app_version)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup Prometheus metrics collection
setup_metrics(app)

app.include_router(appointment_router)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    """Returns service health status."""
    return {"status": "ok", "service": settings.app_name}
