"""Appointment API routes."""

import logging

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import get_current_user_email
from app.models.appointment import Appointment
from app.schemas.appointment import AppointmentCreateRequest, AppointmentResponse

router = APIRouter(prefix="/appointments", tags=["appointments"])
logger = logging.getLogger(__name__)


@router.post("", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
def book_appointment(
    payload: AppointmentCreateRequest,
    current_user: str = Depends(get_current_user_email),
    db: Session = Depends(get_db),
) -> AppointmentResponse:
    """Books a new appointment for an authenticated user."""
    appointment = Appointment(
        patient_id=payload.patient_id,
        doctor_name=payload.doctor_name,
        appointment_time=payload.appointment_time,
        reason=payload.reason,
        booked_by=current_user,
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    logger.info("User %s booked appointment id=%s", current_user, appointment.id)
    return AppointmentResponse(
        id=appointment.id,
        patient_id=appointment.patient_id,
        doctor_name=appointment.doctor_name,
        appointment_time=appointment.appointment_time,
        reason=appointment.reason,
        booked_by=appointment.booked_by,
    )


@router.get("", response_model=list[AppointmentResponse])
def list_appointments(
    current_user: str = Depends(get_current_user_email),
    db: Session = Depends(get_db),
) -> list[AppointmentResponse]:
    """Lists all appointments for authenticated users."""
    logger.info("User %s listed all appointments", current_user)
    appointments = db.scalars(select(Appointment).order_by(Appointment.id)).all()
    return [
        AppointmentResponse(
            id=appointment.id,
            patient_id=appointment.patient_id,
            doctor_name=appointment.doctor_name,
            appointment_time=appointment.appointment_time,
            reason=appointment.reason,
            booked_by=appointment.booked_by,
        )
        for appointment in appointments
    ]
