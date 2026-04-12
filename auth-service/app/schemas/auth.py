"""Pydantic schemas for auth endpoints."""

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """Request payload for user registration."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    """Request payload for user login."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class AuthResponse(BaseModel):
    """Response payload containing access token details."""

    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """Response payload for user identity fields."""

    id: int
    email: EmailStr
