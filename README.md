# Telemedicine Microservices Backend

Production-ready FastAPI microservices scaffold for telemedicine workflows.

## Services

- `auth-service` (port `8000`): register and login users with JWT.
- `patient-service` (port `8001`): list and fetch patient records.
- `appointment-service` (port `8002`): book and list appointments.

Each service includes:

- Modular folder layout: `app`, `routes`, `models`, `schemas`
- `Dockerfile`
- `requirements.txt`
- Input validation using Pydantic
- SQLAlchemy ORM with PostgreSQL
- Alembic database migrations
- Basic logging
- `/health` endpoint

## Environment Setup

1. Copy `.env.example` to `.env`.
2. Set a strong `JWT_SECRET`.
3. Set strong database passwords in `.env`.

Example:

```env
JWT_SECRET=super-strong-secret-value
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60
AUTH_DB_NAME=auth_db
AUTH_DB_USER=auth_user
AUTH_DB_PASSWORD=your-auth-db-password
PATIENT_DB_NAME=patient_db
PATIENT_DB_USER=patient_user
PATIENT_DB_PASSWORD=your-patient-db-password
APPOINTMENT_DB_NAME=appointment_db
APPOINTMENT_DB_USER=appointment_user
APPOINTMENT_DB_PASSWORD=your-appointment-db-password
```

## Run with Docker Compose

```bash
docker compose up --build
```

Each service runs `alembic upgrade head` on startup, so required tables are created automatically.

## Endpoints

### Auth Service

- `POST /auth/register`
- `POST /auth/login`
- `GET /health`

### Patient Service

- `GET /patients` (Bearer token required)
- `GET /patients/{patient_id}` (Bearer token required)
- `GET /health`

### Appointment Service

- `POST /appointments` (Bearer token required)
- `GET /appointments` (Bearer token required)
- `GET /health`

## Quick Test Flow

1. Register user:

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"doctor@example.com","password":"StrongPass123"}'
```

2. Login and get token:

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"doctor@example.com","password":"StrongPass123"}'
```

3. Use token against patient and appointment services:

```bash
curl http://localhost:8001/patients -H "Authorization: Bearer <TOKEN>"
```

```bash
curl -X POST http://localhost:8002/appointments \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"patient_id":1,"doctor_name":"Dr. Smith","appointment_time":"2026-04-15T10:00:00Z","reason":"Routine follow-up"}'
```
