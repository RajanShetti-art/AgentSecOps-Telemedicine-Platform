"""SQLAlchemy model for appointments."""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Appointment(Base):
    """Represents a booked appointment record."""

    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    patient_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    doctor_name: Mapped[str] = mapped_column(String(100), nullable=False)
    appointment_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    reason: Mapped[str] = mapped_column(String(300), nullable=False)
    booked_by: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
