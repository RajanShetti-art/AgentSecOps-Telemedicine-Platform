"""Patient API routes."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import get_current_user_email
from app.models.patient import Patient
from app.schemas.patient import PatientResponse

router = APIRouter(prefix="/patients", tags=["patients"])
logger = logging.getLogger(__name__)


@router.get("", response_model=list[PatientResponse])
def get_all_patients(
    current_user: str = Depends(get_current_user_email),
    db: Session = Depends(get_db),
) -> list[PatientResponse]:
    """Returns all patient records for authenticated users."""
    logger.info("User %s fetched all patients", current_user)
    patients = db.scalars(select(Patient).order_by(Patient.id)).all()
    return [
        PatientResponse(
            id=patient.id,
            full_name=patient.full_name,
            age=patient.age,
            condition=patient.condition,
        )
        for patient in patients
    ]


@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient_by_id(
    patient_id: int,
    current_user: str = Depends(get_current_user_email),
    db: Session = Depends(get_db),
) -> PatientResponse:
    """Returns a single patient record by its ID."""
    patient = db.scalar(select(Patient).where(Patient.id == patient_id))
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    logger.info("User %s fetched patient id=%s", current_user, patient_id)
    return PatientResponse(
        id=patient.id,
        full_name=patient.full_name,
        age=patient.age,
        condition=patient.condition,
    )
