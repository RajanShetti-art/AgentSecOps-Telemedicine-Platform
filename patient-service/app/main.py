"""Patient service application entrypoint."""

from fastapi import FastAPI

from app.config import settings
from app.logging_config import configure_logging
from app.models import patient  # noqa: F401
from app.routes.patients import router as patient_router

configure_logging()
app = FastAPI(title=settings.app_name, version=settings.app_version)
app.include_router(patient_router)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    """Returns service health status."""
    return {"status": "ok", "service": settings.app_name}
