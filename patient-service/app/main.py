"""Patient service application entrypoint."""

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import settings
from app.logging_config import configure_logging
from app.models import patient  # noqa: F401
from app.routes.patients import router as patient_router

configure_logging()
app = FastAPI(title=settings.app_name, version=settings.app_version)
app.include_router(patient_router)

# Expose Prometheus metrics endpoint at /metrics for observability stack.
Instrumentator().instrument(app).expose(app)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    """Returns service health status."""
    return {"status": "ok", "service": settings.app_name}
