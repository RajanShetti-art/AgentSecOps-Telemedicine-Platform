"""Pydantic schemas for patient endpoints."""

from pydantic import BaseModel, Field
from pydantic import ConfigDict


class PatientResponse(BaseModel):
    """Patient data returned by API endpoints."""

    id: int
    full_name: str = Field(min_length=2, max_length=100)
    age: int = Field(ge=0, le=130)
    condition: str = Field(min_length=2, max_length=200)

    model_config = ConfigDict(from_attributes=True)
