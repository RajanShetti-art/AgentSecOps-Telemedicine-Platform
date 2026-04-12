"""Pydantic schemas for appointment endpoints."""

from datetime import datetime

from pydantic import BaseModel, Field
from pydantic import ConfigDict


class AppointmentCreateRequest(BaseModel):
    """Request payload for creating an appointment."""

    patient_id: int = Field(gt=0)
    doctor_name: str = Field(min_length=2, max_length=100)
    appointment_time: datetime
    reason: str = Field(min_length=5, max_length=300)


class AppointmentResponse(BaseModel):
    """Response payload for appointment records."""

    id: int
    patient_id: int
    doctor_name: str
    appointment_time: datetime
    reason: str
    booked_by: str

    model_config = ConfigDict(from_attributes=True)
