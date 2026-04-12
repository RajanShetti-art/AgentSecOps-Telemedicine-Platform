"""Auth API routes."""

import logging
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.models.user import User
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _ensure_secret_configured() -> None:
    """Ensures JWT secret is configured at runtime."""
    if not settings.jwt_secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="JWT secret is not configured",
        )


def _create_access_token(subject: str) -> str:
    """Creates a signed JWT for the provided subject."""
    _ensure_secret_configured()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": subject, "exp": expires_at}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(payload: RegisterRequest, db: Session = Depends(get_db)) -> UserResponse:
    """Registers a new user account with hashed password."""
    existing_user = db.scalar(select(User).where(User.email == str(payload.email)))
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")

    password_hash = pwd_context.hash(payload.password)
    user = User(email=str(payload.email), password_hash=password_hash)
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info("Registered new user: %s", user.email)
    return UserResponse(id=user.id, email=user.email)


@router.post("/login", response_model=AuthResponse)
def login_user(payload: LoginRequest, db: Session = Depends(get_db)) -> AuthResponse:
    """Authenticates a user and returns a JWT access token."""
    user = db.scalar(select(User).where(User.email == str(payload.email)))
    if not user or not pwd_context.verify(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = _create_access_token(subject=str(user.email))
    logger.info("User logged in: %s", user.email)
    return AuthResponse(access_token=token)
