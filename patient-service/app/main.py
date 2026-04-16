"""Patient service application entrypoint."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import func, select

from app.config import settings
from app.db import SessionLocal
from app.logging_config import configure_logging
from app.models import patient  # noqa: F401
from app.models.patient import Patient
from app.routes.patients import router as patient_router

configure_logging()
logger = logging.getLogger(__name__)
app = FastAPI(title=settings.app_name, version=settings.app_version)


def _seed_patients_if_empty() -> None:
    """Seeds baseline patient records for local/demo usage if table is empty."""
    with SessionLocal() as db:
        total_patients = db.scalar(select(func.count(Patient.id))) or 0
        if total_patients > 0:
            return

        db.add_all(
            [
                Patient(full_name="John Carter", age=45, condition="Hypertension"),
                Patient(full_name="Asha Nair", age=32, condition="Asthma"),
                Patient(full_name="Maya Thomas", age=58, condition="Type 2 Diabetes"),
            ]
        )
        db.commit()
        logger.info("Seeded baseline patient records")


@app.on_event("startup")
def startup_seed_data() -> None:
    """Initializes baseline data needed by the UI flow."""
    _seed_patients_if_empty()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(patient_router)

# Expose Prometheus metrics endpoint at /metrics for observability stack.
Instrumentator().instrument(app).expose(app)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    """Returns service health status."""
    return {"status": "ok", "service": settings.app_name}
